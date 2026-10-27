"""Telefon ma'lumotnomasi API'si. Interfeys alohida: frontend/ (Vue).

Ishga tushirish: uvicorn --factory app.main:create_app
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.admin import router as admin_router
from app.config import Settings, load_settings
from app.db import init_db
from app.public import router as public_router

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db(settings.db_path)
        yield

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="telefon_session",
        max_age=8 * 3600,
        same_site="lax",
        https_only=settings.cookie_secure,
    )

    @app.middleware("http")
    async def require_xhr_header(request: Request, call_next):
        # CSRF himoyasi: boshqa saytdagi forma bu sarlavhani qo'ya olmaydi,
        # brauzer esa uni preflight'siz boshqa domenga yubormaydi.
        if (
            request.method not in SAFE_METHODS
            and request.url.path.startswith("/api/")
            and request.headers.get("x-requested-with") != "XMLHttpRequest"
        ):
            return JSONResponse({"detail": "So'rov rad etildi."}, status_code=403)
        return await call_next(request)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse({"detail": "Ma'lumot noto'g'ri yuborildi."}, status_code=422)

    app.include_router(public_router)
    app.include_router(admin_router)
    return app
