import cloudinary, cloudinary.uploader
from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

async def upload_avatar(fileobj, public_id: str):
    # fileobj = SpooledTemporaryFile из UploadFile.file
    res = cloudinary.uploader.upload(fileobj, public_id=public_id, folder="avatars", overwrite=True)
    return res["secure_url"]
