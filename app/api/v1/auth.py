from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserRegistration, UserLogin, UserDetails
from app.services.auth import register_user
from app.services.auth import UserAuthentication, get_user_list
from app.dependencies import get_user_authentication, get_async_session
from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    user: UserRegistration, db: AsyncSession = Depends(get_async_session)
):
    try:
        user = await register_user(user, db)
        return Response(
            status_code=status.HTTP_201_CREATED,
            content={"message": "User registered successfully", "data": user},
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login")
async def login(
    credentials: UserLogin,
    response: Response,
    auth_service: UserAuthentication = Depends(get_user_authentication),
):
    tokens = await auth_service.login(credentials)

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
    )

    return Response(status_code=status.HTTP_200_OK, content=tokens)


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: UserAuthentication = Depends(get_user_authentication),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    new_tokens = await auth_service.refresh_token(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_tokens["refresh_token"],
        httponly=True,
        secure=True,
    )

    return Response(status_code=status.HTTP_200_OK, content=new_tokens)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    auth_service: UserAuthentication = Depends(get_user_authentication),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.logout(refresh_token)

    response.delete_cookie("refresh_token")
    return Response(
        status_code=status.HTTP_200_OK, content={"detail": "Successfully logged out"}
    )


@router.get("/users", response_model=List[UserDetails])
async def get_users(
    db: AsyncSession = Depends(get_async_session),
):
    users = await get_user_list(db)
    return users
