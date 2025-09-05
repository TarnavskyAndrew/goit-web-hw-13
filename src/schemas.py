from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime


# -------- USER ----------
class UserModel(BaseModel):
    username: Optional[str] = Field(default=None, min_length=2, max_length=32)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class UserDb(BaseModel):
    id: int
    username: Optional[str]
    email: EmailStr
    created_at: datetime
    avatar: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


# class UserResponse(BaseModel):
#     user: UserDb
#     detail: str = "User successfully created"


class UserResponse(BaseModel):
    id: int | None = None
    username: str
    email: EmailStr
    created_at: datetime | None = None
    avatar: str | None = None
    role: str | None = None
    confirmed: bool | None = None

    class Config:
        from_attributes = True


class RoleUpdate(BaseModel):
    role: str


# --------- AUTH ---------
class SignupResponse(BaseModel):
    user: UserResponse
    detail: str = "User created. Check your email."


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr

    model_config = {"json_schema_extra": {"example": {"email": "user@example.com"}}}


class ResetPasswordModel(BaseModel):
    new_password: str


# -------- CONTACT ----------
class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    extra: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True


# -------- DEBUG ----------
class DebugEmailRequest(BaseModel):
    email: EmailStr
