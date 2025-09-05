from fastapi import APIRouter, Request, Depends
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import inspect

from src.database.db import get_db
from src.services.email import send_email
from src.schemas import DebugEmailRequest


router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/send")
async def debug_send(
    body: DebugEmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    link = f"{str(request.base_url)}debug/ok"
    await send_email(
        email=body.email,
        username="debug",
        link=link,
        template_name="email_template.html",
    )
    return {"ok": True}


@router.get("/__routes")
async def debug_routes(request: Request):
    """
    Список усіх маршрутів додатків з файлами та рядками.
    """
    app = request.app
    items = []

    for r in app.routes:
        if isinstance(r, APIRoute):
            fn = r.endpoint
            try:
                file = inspect.getsourcefile(fn)
                line = inspect.getsourcelines(fn)[1] if file else None
            except (OSError, TypeError):
                file, line = None, None

            items.append(
                {
                    "path": r.path,
                    "methods": sorted(list(r.methods)),
                    "endpoint": f"{fn.__module__}.{fn.__name__}",
                    "file": file,
                    "line": line,
                    "tags": r.tags,
                    "summary": r.summary,
                }
            )

    return {"routes": items}
