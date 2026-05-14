from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")

routers = [
    auth_router,
    # add other routers here in the future
]

for router in routers:
    api_router.include_router(router)



