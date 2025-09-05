from sqlalchemy import text
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db


router = APIRouter(prefix="/health", tags=["System"])

# перевірка стану сервісу

# @router.get("/")
# def healthchecker():
#     return {"message": "Welcome to FastAPI Contacts API"}


@router.get("/", summary="Healthcheck")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1")) # Виконуємо простий запит до бази даних
        if result.fetchone() is None:  # Перевіряємо, чи запит повернув результат
            raise HTTPException( 
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not available",
            )
        return {"status": "ok", "db": "ok"} 
    except Exception: 
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available",
        )
