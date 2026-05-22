from fastapi import FastAPI
from app.api.v1.api_router import api_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="FastAPI Todo App")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
