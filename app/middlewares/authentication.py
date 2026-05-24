from typing import Optional

from starlette.requests import Request
from fastapi import Depends, Security
from fastapi.security import (
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from app.models.user import User
from app.dependencies import get_user_authentication
from app.services.auth import JwtService
from sqlalchemy.future import select
from app.core.logger import logger

basic_security = HTTPBasic(auto_error=False)
bearer_security = HTTPBearer(auto_error=False)


async def authentication_dependency(
    request: Request,
    credentials: Optional[HTTPBasicCredentials] = Security(basic_security),
    token_credentials: Optional[HTTPAuthorizationCredentials] = Security(
        bearer_security
    ),
    user_authentication: JwtService = Depends(get_user_authentication),
) -> None:
    """Dependency function to retrieve the authenticated user from the request state.

    Args:
        request (Request): The incoming HTTP request.
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials extracted from the request.
        token_credentials (HTTPBasicCredentials): The HTTP basic credentials extracted from the request.
        jwt_service (JwtService): The JWT service for token validation.
    Returns:
        None: This function does not return anything, but raises an HTTPException if the user is
    Raises:
        HTTPException: If the user is not authenticated.
    """
    try:
        access_token = None
        request.state.user = None
        if token_credentials:
            access_token = token_credentials.credentials
        elif credentials:
            username = credentials.username
            password = credentials.password
            user = await user_authentication.authenticate_user(username, password)
            tokens = await user_authentication.create_tokens(user)
            access_token = tokens["access_token"]
        if not access_token:
            return
        decoded_token = user_authentication.jwt_decode(access_token)
        user_id = decoded_token.get("user_id")
        user_instance = await user_authentication.db.execute(
            select(User).where(User.id == user_id)
        )
        user_instance = user_instance.scalar_one_or_none()
        request.state.user = user_instance
    except Exception as e:
        request.state.user = None
        logger.error(f"Authentication failed: {str(e)}")
