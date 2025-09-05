from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi.templating import Jinja2Templates
import redis.asyncio as redis
import logging
import os, sys
from datetime import datetime

from src.conf.config import settings
from src.routes import contacts, health, auth, users, debug
from src.core.error_handlers import init_exception_handlers
from src.middleware import setup_middlewares


print(
    "### BOOT:",
    __file__,
    "cwd=",
    os.getcwd(),
    "py=",
    sys.executable,
    "ts=",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    app.state.redis = await redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(app.state.redis)  # Ініціалізація лімітерів

    try:
        yield  # працює FastAPI
    finally:
        await app.state.redis.close()


# Створюємо додаток (ASGI-додаток на базі Starlette)
app = FastAPI(
    title="Contacts Service API",
    description="API for contact management with JWT authentication: CRUD, search, birthdays.",
    version="2.0.0",
    lifespan=lifespan_handler,
)

# init_exception_handlers(app)  # Підключення глобальних хендлерів

setup_middlewares(app)  # подключаем middlewares

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(health.router, prefix="/system")
app.include_router(debug.router, prefix="/api")


# uvicorn main:app --reload
# poetry run uvicorn main:app --reload --log-level debug
# http://127.0.0.1:8000/docs
