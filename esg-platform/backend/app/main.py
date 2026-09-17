"""
ESG Intelligence & Carbon Accounting Platform — FastAPI application factory.

Phase 1 sets up:
  - Application lifecycle (startup / shutdown)
  - CORS middleware
  - Security headers middleware
  - Centralised exception handlers
  - API v1 router
  - Root health alias
  - OpenAPI documentation

Secrets are NEVER hardcoded. All configuration is sourced from
app.core.config.Settings (environment variables / .env file).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    ESGBaseException,
    esg_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging

# Initialise structured logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


# ── Lifespan (replaces on_event) ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown logic.

    Startup tasks (Phase 1 — minimal):
      - Log confirmation that the application started.

    Future phases will add:
      - Database connection pool warm-up
      - Supabase client initialisation
      - Redis/Celery connection validation
      - Pre-loading emission factor cache
    """
    logger.info(
        "Starting %s v%s [env=%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT,
    )

    # Create all tables on startup (safe no-op if they already exist).
    # Models are already loaded transitively via the router imports above.
    # For production, use Alembic migrations instead.
    from app.db.session import engine
    from app.db.base_class import Base
    import app.models  # noqa: F401 — ensure all models are registered
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified / created.")

    yield
    logger.info("Shutting down %s", settings.APP_NAME)


# ── Security headers middleware ───────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds defensive HTTP security headers to every response.
    These are baseline headers; a proper reverse proxy (nginx/Caddy)
    should also set Strict-Transport-Security in production.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        return response


# ── Application factory ───────────────────────────────────────────────────────

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-powered ESG intelligence and carbon accounting platform. "
            "Scope 1 / 2 / 3 GHG calculations, ESG scoring, compliance "
            "mapping, document AI, and RAG-powered ESG assistant."
        ),
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Security headers ──────────────────────────────────────────────────────
    app.add_middleware(SecurityHeadersMiddleware)

    # ── Exception handlers ────────────────────────────────────────────────────
    from fastapi import HTTPException
    from starlette.exceptions import HTTPException as StarletteHTTPException

    app.add_exception_handler(ESGBaseException, esg_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

    # ── API routers ───────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── Root health alias (for load-balancer probes) ──────────────────────────
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def root_health():
        return {"status": "healthy"}

    # ── Root redirect info ────────────────────────────────────────────────────
    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": f"{settings.API_V1_PREFIX}/docs",
        }

    logger.info("Application configured. CORS origins: %s", settings.BACKEND_CORS_ORIGINS)
    return app


app = create_application()
