import re

from click import File
from fastapi import APIRouter, Depends, File, Request, Form, UploadFile
from pydantic_core import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import UserDetails, UserRegister
from app.services.auth import get_user_list
from app.dependencies import get_async_session
from typing import Any, List, Annotated
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


async def drf_nested_form_parser(request: Request) -> dict[str, Any]:
    """
    Parses flat form data keys like 'profile[first_name]' or 'profile.first_name' 
    and converts them into a nested Python dictionary structure.
    """
    form_data = await request.form()
    print("Raw form data:", form_data)  # Debugging statement to see the raw form data
    parsed_dict: dict[str, Any] = {}

    for key, value in form_data.items():
        # Match bracket notation: profile[first_name]
        bracket_match = re.match(r"^(\w+)\[(\w+)\]$", key)
        # Match dot notation: profile.first_name
        dot_match = re.match(r"^(\w+)\.(\w+)$", key) if not bracket_match else None

        if bracket_match or dot_match:
            match = bracket_match or dot_match
            parent_key, child_key = match.groups()
            
            if parent_key not in parsed_dict:
                parsed_dict[parent_key] = {}
                
            parsed_dict[parent_key][child_key] = value
        else:
            # Flat top-level keys (username, email)
            parsed_dict[key] = value

    return parsed_dict

@permissioned_router.post("/register")
async def register_user(form_payload: UserRegister = Depends(drf_nested_form_parser)):
    try:
        # Validate the dynamically built dictionary against our Pydantic schema
        user_data = UserRegister(**form_payload)
    except ValidationError as e:
        # Returns standard FastAPI 422 errors if validation fails
        print(e.errors())
        raise

    # You now have type hints and direct access to your file!
    filename = user_data.profile.profile_picture.filename
    
    return {
        "status": "success",
        "username": user_data.username,
        "profile": {
            "first_name": user_data.profile.first_name,
            "age": user_data.profile.age,
            "avatar_filename": filename
        }
    }


router.include_router(permissioned_router)