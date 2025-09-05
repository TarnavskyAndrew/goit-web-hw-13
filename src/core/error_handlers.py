from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette import status

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Імпортуємо помилку унікальності з psycopg2, якщо доступна
try:    
    from psycopg2.errors import UniqueViolation 
except (Exception): 
    UniqueViolation = None  # type: ignore


# Функція для формування єдиного формату помилки у відповідях API
def _error_payload(
    code: int,
    message: str,
    request: Request,
    *,
    details: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:

    """Єдиний формат помилки y всіх відповідях."""

    payload: Dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "path": str(request.url.path),
            "method": request.method,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    }
    if details is not None: # якщо є деталі помилки
        payload["error"]["details"] = details
    return payload


# Підключаємо глобальні обробники до програми
def init_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, exc: RequestValidationError):
        # 422: помилки валідації Pydantic (body/query/path)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload(
                422, "Validation failed", request, details=exc.errors()
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def on_http_exception(request: Request, exc: StarletteHTTPException):
        # Будь-які raise HTTPException(...): 400/401/403/404/405 и т.д.
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                exc.status_code, str(exc.detail or "HTTP error"), request
            ),
        )

    @app.exception_handler(IntegrityError)
    async def on_integrity_error(request: Request, exc: IntegrityError):
        # 409: Порушення унікальності; інакше 400: інші обмеження цілісності
        is_unique = bool(
            UniqueViolation and isinstance(getattr(exc, "orig", None), UniqueViolation)
        )
        code = status.HTTP_409_CONFLICT if is_unique else status.HTTP_400_BAD_REQUEST
        msg = (
            "Duplicate value violates unique constraint"
            if is_unique
            else "Database integrity error"
        )
        return JSONResponse(
            status_code=code, content=_error_payload(code, msg, request)
        )

    @app.exception_handler(SQLAlchemyError)
    async def on_sa_error(request: Request, exc: SQLAlchemyError):
        # 500: інші помилки БД/ORM
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(500, "Database error", request),
        )

    @app.exception_handler(Exception)
    async def on_unhandled(request: Request, exc: Exception):
        # 500: все інше
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(500, "Internal server error", request),
        )
