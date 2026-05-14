# from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import (
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
)

DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Create the asynchronous engine and session maker
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# async def initialize_database():
#     """
#     Function to initialize the database by creating all tables defined in the SQLModel metadata.
#     """
#     async with engine.begin() as conn:
#         await conn.run_sync(SQLModel.metadata.create_all)