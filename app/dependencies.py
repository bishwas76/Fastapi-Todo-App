from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_maker
from typing import AsyncGenerator
from app.services.auth import UserAuthentication
from fastapi import Depends


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_user_authentication(
    db: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[UserAuthentication, None]:
    yield UserAuthentication(db)
