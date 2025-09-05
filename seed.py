import asyncio
from sqlalchemy import select

from src.database.db import session
from src.database.models import User
from src.services.auth import auth_service
from src.conf.config import settings


ADMIN_EMAIL = settings.ADMIN_EMAIL
ADMIN_PASSWORD = settings.ADMIN_PASSWORD

# Скрипт для створення адміністратора при першому запуску
async def create_admin():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise ValueError("Please set ADMIN_EMAIL and ADMIN_PASSWORD in .env")

    async with session() as db:
        res = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
        user = res.scalar_one_or_none()

        if user:
            print(f"User {ADMIN_EMAIL} already exists (role={user.role})")
            return

        pwd_hash = auth_service.get_password_hash(ADMIN_PASSWORD)
        admin = User(
            username="admin", email=ADMIN_EMAIL, password=pwd_hash, role="admin"
        )
        db.add(admin)
        await db.commit()
        print(f"Admin {ADMIN_EMAIL} created. Password: {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(create_admin())


# poetry run python seed.py
