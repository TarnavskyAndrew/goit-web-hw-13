import json
import redis.asyncio as redis
import logging

from src.conf.config import settings
from src.schemas import UserResponse


logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    encoding="utf-8",
    decode_responses=True,
)

CACHE_EXPIRE_SECONDS = 300  # 5 хвилин


# Функція для кешування користувача
async def cache_user(user):
    key = f"user:{user.email}"
    value = json.dumps(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": str(user.created_at),  # стр для JSON
            "avatar": user.avatar,
            "role": user.role,
        }
    )
    await redis_client.set(key, value, ex=CACHE_EXPIRE_SECONDS)
    logger.info(f"USER cached in Redis (set): {user.email}")


# Функція для отримання користувача з кешу
async def get_cached_user(email: str):
    key = f"user:{email}"
    value = await redis_client.get(key)
    if value:
        data = json.loads(value)
        # повертаємо Pydantic модель
        logger.info(f"USER fetched from Redis (get): {email}")
        return UserResponse(**data)
    return None
