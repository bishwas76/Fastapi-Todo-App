from fastapi import APIRouter, Depends
from app.api.v1.auth import (
    router as auth_router,
)
from app.api.v1.user import (
    router as user_router,
)
from app.middlewares.authentication import authentication_dependency

api_router = APIRouter(prefix="/api/v1")

protected_gateway = APIRouter(dependencies=[Depends(authentication_dependency)])
public_gateway = APIRouter()

pubic_routers = [
    auth_router,
    # add other routers here in the future for public access
]
protected_routers = [
    user_router,
    # add protected routers here in the future
]

for router in pubic_routers:
    public_gateway.include_router(router)

for protected_router in protected_routers:
    protected_gateway.include_router(protected_router)


api_router.include_router(public_gateway)
api_router.include_router(protected_gateway)