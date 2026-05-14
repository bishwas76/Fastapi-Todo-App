from sqlmodel import Field, SQLModel
from datetime import datetime
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

pwd_context = PasswordHash((BcryptHasher(),))

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str = Field(exclude=True)
    first_name: str = Field(default=None)
    middle_name: str = Field(nullable=True)
    last_name: str = Field(default=None)
    is_active: bool = Field(default=True)
    last_login: datetime = Field(nullable=True)
    is_superuser: bool = Field(default=False)
    
    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)


class OutstandingToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    jti: str = Field(index=True, unique=True)
    token: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(nullable=False)


class BlacklistedToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    token: int = Field(foreign_key="outstandingtoken.id")
    blacklisted_at: datetime = Field(default_factory=datetime.utcnow)