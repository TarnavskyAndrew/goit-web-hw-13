from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import cloudinary, cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.schemas import RoleUpdate, UserDb
from src.repository.users import list_users, set_role
from src.services.permissions import access_admin_only, Role
from src.services.auth import auth_service
from src.services.storage import upload_avatar
from src.conf.config import settings
from src.repository import users as repository_users


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserDb], dependencies=[Depends(access_admin_only)])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await list_users(db)


@router.patch(
    "/{user_id}/role",
    summary="Change user role (Available only for admin)",
    response_model=UserDb,
    dependencies=[Depends(access_admin_only)],
)
# async def change_role(user_id: int, role: Role, db: AsyncSession = Depends(get_db)):
#     user = await set_role(user_id, role.value, db)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


async def change_role(
    user_id: int, body: RoleUpdate, db: AsyncSession = Depends(get_db)
):
    user = await repository_users.set_role(user_id, body.role, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/avatar", status_code=200)
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current: User = Depends(auth_service.get_current_user),
):
    if file.content_type not in ("image/png", "image/jpeg", "image/jpg", "image/webp"):
        raise HTTPException(status_code=415, detail="Unsupported media type")
    # url = await upload_avatar(file.file, public_id=f"user_{current.id}")
    url = await upload_avatar(file.file, public_id=f"ContactsAPI/{current.username}")
    current.avatar = url
    await db.commit()
    return {"avatar_url": url}


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(
    file: UploadFile = File(...),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    r = cloudinary.uploader.upload(
        file.file, public_id=f"ContactsAPI/{current_user.username}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f"ContactsAPI/{current_user.username}"
    ).build_url(width=250, height=250, crop="fill", version=r.get("version"))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
