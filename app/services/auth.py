from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, OutstandingToken, BlacklistedToken
from app.schemas.auth import UserRegistration, UserLogin
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.core.config import (
    SECRET_KEY,
    JWT_ENCRYPTION_ALGORITHM,
    JWT_TOKEN_EXPIRE_MINUTES,
)
import jwt
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import uuid


async def get_user_by_email(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_list(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()


async def register_user(user_data: UserRegistration, db: AsyncSession):
    email = user_data.email
    existing_user = await get_user_by_email(email, db)
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered."
        )
    user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        middle_name=user_data.middle_name,
        last_name=user_data.last_name,
    )
    user.set_password(user_data.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class JwtService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def get_pclaim(user: User) -> str | None:
        # Take the last 15 characters of the hashed password as a validator claim.
        # If the password changes, this string changes, inherently invalidating old tokens.
        try:
            claim = user.password[-15:]
            bclaim = claim.encode("utf-8")
            pclaim = str(int.from_bytes(bclaim, "big"))
            return pclaim
        except Exception as e:
            return None

    async def create_tokens(self, user: User, custom_claims: dict = None):
        if custom_claims is None:
            custom_claims = {}

        pclaim = self.get_pclaim(user)

        access_exp = datetime.utcnow() + timedelta(minutes=JWT_TOKEN_EXPIRE_MINUTES)
        access_jti = str(uuid.uuid4())
        access_payload = {
            "token_type": "access",
            "exp": access_exp,
            "jti": access_jti,
            "user_id": user.id,
            "pclaim": pclaim,
            **custom_claims,
        }
        access_token = jwt.encode(
            access_payload, SECRET_KEY, algorithm=JWT_ENCRYPTION_ALGORITHM
        )

        refresh_exp = datetime.utcnow() + timedelta(days=7)
        refresh_jti = str(uuid.uuid4())
        refresh_payload = {
            "token_type": "refresh",
            "exp": refresh_exp,
            "jti": refresh_jti,
            "user_id": user.id,
            "pclaim": pclaim,
        }
        refresh_token = jwt.encode(
            refresh_payload, SECRET_KEY, algorithm=JWT_ENCRYPTION_ALGORITHM
        )

        outstanding = OutstandingToken(
            user_id=user.id,
            jti=refresh_jti,
            token=refresh_token,
            expires_at=refresh_exp,
        )
        self.db.add(outstanding)

        # set last login date
        user.last_login = datetime.utcnow()
        self.db.add(user)

        await self.db.commit()

        return {
            "token_type": "bearer",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def jwt_decode(token: str):
        try:
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=[JWT_ENCRYPTION_ALGORITHM]
            )
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def blacklist_refresh_token(self, token_str: str):
        payload = self.jwt_decode(token_str)
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=400, detail="Only refresh tokens can be blacklisted"
            )

        jti = payload.get("jti")
        result = await self.db.execute(
            select(OutstandingToken).where(OutstandingToken.jti == jti)
        )
        outstanding = result.scalar_one_or_none()

        if outstanding:
            b_result = await self.db.execute(
                select(BlacklistedToken).where(BlacklistedToken.token == outstanding.id)
            )
            if b_result.scalar_one_or_none():
                raise HTTPException(status_code=401, detail="Token already blacklisted")

            new_blacklist = BlacklistedToken(token=outstanding.id)
            self.db.add(new_blacklist)
            await self.db.commit()

    async def verify_and_refresh(self, refresh_token_str: str):
        payload = self.jwt_decode(refresh_token_str)
        if payload.get("token_type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        jti = payload.get("jti")
        result = await self.db.execute(
            select(OutstandingToken).where(OutstandingToken.jti == jti)
        )
        outstanding = result.scalar_one_or_none()

        if not outstanding:
            raise HTTPException(status_code=401, detail="Token not found")

        b_result = await self.db.execute(
            select(BlacklistedToken).where(BlacklistedToken.token == outstanding.id)
        )
        if b_result.scalar_one_or_none():
            raise HTTPException(status_code=401, detail="Refresh token is blacklisted")

        u_result = await self.db.execute(
            select(User).where(User.id == outstanding.user_id)
        )
        user = u_result.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        if payload.get("pclaim") != self.get_pclaim(user):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid. Password may have changed.",
            )

        blacklist = BlacklistedToken(token=outstanding.id)
        self.db.add(blacklist)

        new_tokens = await self.create_tokens(
            user, custom_claims={"email": user.email, "is_superuser": user.is_superuser}
        )

        # set last login date
        user.last_login = datetime.utcnow()
        self.db.add(user)

        return new_tokens


class UserAuthentication(JwtService):
    def __init__(self, db: AsyncSession, custom_claims: dict = None):
        super().__init__(db)
        self.custom_claims = custom_claims

    async def authenticate_user(self, email: str, password: str):
        user = await get_user_by_email(email, self.db)
        if not user or not user.verify_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def login(self, credentials: UserLogin):
        user = await self.authenticate_user(credentials.username, credentials.password)
        tokens = await self.create_tokens(user, custom_claims=self.custom_claims)
        return tokens

    async def logout(self, refresh_token_str: str):
        await self.blacklist_refresh_token(refresh_token_str)

    async def refresh_token(self, refresh_token_str: str):
        new_tokens = await self.verify_and_refresh(refresh_token_str)
        return new_tokens
