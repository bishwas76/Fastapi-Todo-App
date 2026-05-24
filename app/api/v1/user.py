from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserDetails
from app.services.auth import get_user_list
from app.dependencies import get_async_session
from typing import List
from app.core.logger import logger
from app.core.permissions import AllowAny

router = APIRouter(prefix="/users", tags=["users"])
permissioned_router = APIRouter(dependencies=[Depends(AllowAny())])

@router.get("/list", response_model=List[UserDetails])
async def get_users(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
):
    users = await get_user_list(db)

    logger.info(f"Retrieved {len(users)} users from the database")

    return users

router.include_router(permissioned_router)