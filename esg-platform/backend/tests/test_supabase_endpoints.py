"""
Integration tests for Supabase API endpoints (/api/v1/supabase/*).
"""

import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.services.storage import storage_service


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_supabase_status_endpoint(client):
    """GET /api/v1/supabase/status should return structured diagnostic JSON."""
    response = await client.get("/api/v1/supabase/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "supabase" in data
    assert "database" in data
    assert "config" in data


@pytest.mark.asyncio
async def test_ensure_bucket_endpoint(client):
    """POST /api/v1/supabase/ensure-bucket should verify storage bucket."""
    with patch.object(storage_service, "ensure_bucket_exists", return_value=True):
        response = await client.post("/api/v1/supabase/ensure-bucket?bucket_name=esg-documents")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["bucket"] == "esg-documents"
