from fastapi import FastAPI
from app.api.v1.api_router import api_router

# from app.db.database import initialize_database

# from contextlib import asynccontextmanager

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Initialize the database before the application starts
#     await initialize_database()
#     yield
#     # You can add any cleanup code here if needed when the application shuts down
# lifespan=lifespan

app = FastAPI(title="FastAPI Todo App")

app.include_router(api_router)



