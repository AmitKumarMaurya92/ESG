"""
Phase 1 tests — health endpoint and application bootstrap.

Run with:
    cd backend
    pytest tests/ -v
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Async test client wrapping the FastAPI app."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


# ── Health endpoint tests ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_root_alias(client):
    """GET /health (root alias) must return 200 with status=healthy."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_v1(client):
    """GET /api/v1/health must return full health response."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_uptime_is_numeric(client):
    """uptime_seconds must be a non-negative number."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """GET / must return app name and docs URL."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "docs" in data


# ── Error handling tests ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_404_returns_structured_error(client):
    """Unknown routes must return a structured JSON error."""
    response = await client.get("/api/v1/nonexistent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data


# ── Security header tests ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_security_headers_present(client):
    """Security headers must be present on all responses."""
    response = await client.get("/health")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
