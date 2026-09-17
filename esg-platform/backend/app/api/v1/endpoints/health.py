"""
Health-check endpoint.

GET /api/v1/health
GET /health          (root-level alias registered in main.py)

Returns the application status, version, and environment.
Used by load balancers, Docker health checks, and monitoring tools.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()

# Record when this process started (used to calculate uptime)
_PROCESS_START = time.time()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    uptime_seconds: float
    timestamp: str


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns the current health status of the API. "
        "A 200 response indicates the service is running normally."
    ),
    responses={
        200: {"description": "Service is healthy"},
        503: {"description": "Service is unavailable"},
    },
)
async def health_check() -> HealthResponse:
    """
    Lightweight liveness probe.

    This endpoint does NOT perform database or external-service checks
    (those are handled by a separate /readiness endpoint added in a
    later phase). It simply confirms the process is alive and the
    configuration is loaded.
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=round(time.time() - _PROCESS_START, 2),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
