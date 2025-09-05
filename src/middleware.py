import time
from fastapi import Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware


# Middleware для вимірювання часу обробки запиту
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)  # додаємо в headers
    return response


def setup_middlewares(app):
    # реєструємо кастомний middleware
    app.middleware("http")(add_process_time_header)  # додавати нові middleware сюда ->

    # реєструємо CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # або обмежити до спусику: ["http://localhost:3000"]
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
