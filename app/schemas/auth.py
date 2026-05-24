from datetime import datetime

from pydantic import EmailStr, model_validator, Field
from typing import Optional
from fastapi import HTTPException, status
from app.core.schema import BaseCamelModel

class UserRegistration(BaseCamelModel):
    username: Optional[str] = Field(default=None, json_schema_extra={"readOnly": True})
    email: EmailStr
    password: str
    password_confirm: str
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_passwords(cls, values):
        password = values.password
        password_confirm = values.password_confirm
        if password != password_confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
            )
        return values

    @model_validator(mode="after")
    def sync_username_email(self):
        if not self.username:
            self.username = self.email
        return self


class UserLogin(BaseCamelModel):
    username: EmailStr
    password: str


class UserDetails(BaseCamelModel):
    id: int
    username: EmailStr
    email: EmailStr
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
