"""
Unit tests for Supabase Storage service (backend/app/services/storage.py).
"""

import pytest
from unittest.mock import MagicMock, patch
from app.services.storage import SupabaseStorageService


@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    # Mock storage bucket operations
    mock_bucket = MagicMock()
    mock_bucket.name = "esg-documents"
    client.storage.list_buckets.return_value = [mock_bucket]
    
    mock_storage_bucket = MagicMock()
    mock_storage_bucket.upload.return_value = {"path": "test/file.pdf"}
    mock_storage_bucket.download.return_value = b"test content"
    mock_storage_bucket.create_signed_url.return_value = {"signedUrl": "https://signed.url/test.pdf"}
    mock_storage_bucket.remove.return_value = True
    mock_storage_bucket.list.return_value = [{"name": "file.pdf"}]

    client.storage.from_.return_value = mock_storage_bucket
    return client


def test_ensure_bucket_exists(mock_supabase_client):
    service = SupabaseStorageService(bucket_name="esg-documents")
    with patch.object(service, "_get_client", return_value=mock_supabase_client):
        res = service.ensure_bucket_exists()
        assert res is True


def test_upload_file(mock_supabase_client):
    service = SupabaseStorageService(bucket_name="esg-documents")
    with patch.object(service, "_get_client", return_value=mock_supabase_client):
        res = service.upload_file("test/doc.pdf", b"pdf data", "application/pdf")
        assert res["success"] is True
        assert res["path"] == "test/doc.pdf"


def test_download_file(mock_supabase_client):
    service = SupabaseStorageService(bucket_name="esg-documents")
    with patch.object(service, "_get_client", return_value=mock_supabase_client):
        content = service.download_file("test/doc.pdf")
        assert content == b"test content"


def test_get_signed_url(mock_supabase_client):
    service = SupabaseStorageService(bucket_name="esg-documents")
    with patch.object(service, "_get_client", return_value=mock_supabase_client):
        url = service.get_signed_url("test/doc.pdf")
        assert "https://signed.url" in url


def test_delete_file(mock_supabase_client):
    service = SupabaseStorageService(bucket_name="esg-documents")
    with patch.object(service, "_get_client", return_value=mock_supabase_client):
        success = service.delete_file("test/doc.pdf")
        assert success is True


def test_list_files(mock_supabase_client):
    service = SupabaseStorageService(bucket_name="esg-documents")
    with patch.object(service, "_get_client", return_value=mock_supabase_client):
        files = service.list_files("folder")
        assert len(files) == 1
        assert files[0]["name"] == "file.pdf"
