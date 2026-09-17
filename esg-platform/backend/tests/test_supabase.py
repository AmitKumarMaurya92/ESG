"""
Unit tests for Supabase core module (backend/app/core/supabase.py).
"""

import pytest
from unittest.mock import patch, MagicMock

from app.core.supabase import (
    get_supabase_client,
    get_supabase_anon_client,
    check_supabase_connection,
    reset_supabase_clients,
)


@pytest.fixture(autouse=True)
def reset_client_cache():
    reset_supabase_clients()
    yield
    reset_supabase_clients()


def test_get_supabase_client_creation():
    """Verify that get_supabase_client instantiates a Client instance."""
    with patch("app.core.supabase.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        
        client = get_supabase_client()
        assert client == mock_client
        mock_create.assert_called_once()


def test_get_supabase_anon_client_creation():
    """Verify that get_supabase_anon_client returns anon client instance."""
    with patch("app.core.supabase.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client

        client = get_supabase_anon_client()
        assert client == mock_client
        mock_create.assert_called_once()


def test_check_supabase_connection_returns_dict():
    """check_supabase_connection should return structured status dictionary."""
    status = check_supabase_connection()
    assert isinstance(status, dict)
    assert "configured" in status
    assert "has_anon_key" in status
    assert "has_service_role_key" in status
    assert "storage_bucket" in status
    assert "details" in status
