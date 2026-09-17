import logging
from typing import List, Dict, Any, Optional
from app.core.supabase import get_supabase_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """
    Service wrapper for interacting with Supabase Storage buckets.
    Handles uploading ESG invoices, regulatory documents, and generated reports.
    """

    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or settings.STORAGE_BUCKET

    def _get_client(self):
        return get_supabase_client()

    def ensure_bucket_exists(self, bucket_name: Optional[str] = None, is_public: bool = False) -> bool:
        """
        Verify that the storage bucket exists, creating it if necessary.
        """
        target_bucket = bucket_name or self.bucket_name
        client = self._get_client()
        try:
            buckets = client.storage.list_buckets()
            existing_buckets = [b.name for b in buckets] if buckets else []
            if target_bucket not in existing_buckets:
                logger.info("Bucket %s does not exist. Creating bucket...", target_bucket)
                client.storage.create_bucket(target_bucket, options={"public": is_public})
            return True
        except Exception as e:
            logger.error("Failed to ensure storage bucket '%s': %s", target_bucket, e)
            return False

    def upload_file(
        self,
        file_path: str,
        file_bytes: bytes,
        content_type: str = "application/octet-stream",
        bucket_name: Optional[str] = None,
        upsert: bool = True,
    ) -> Dict[str, Any]:
        """
        Upload binary content to Supabase Storage.
        
        :param file_path: Path/key inside the bucket (e.g. 'org-123/invoices/2026-09.pdf')
        :param file_bytes: File contents as bytes
        :param content_type: MIME type
        :param bucket_name: Target bucket (defaults to settings.STORAGE_BUCKET)
        :param upsert: Overwrite if file exists
        :return: Supabase response payload
        """
        target_bucket = bucket_name or self.bucket_name
        client = self._get_client()
        try:
            response = client.storage.from_(target_bucket).upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": content_type, "x-upsert": str(upsert).lower()},
            )
            logger.info("Successfully uploaded file %s to bucket %s", file_path, target_bucket)
            return {"success": True, "path": file_path, "response": response}
        except Exception as e:
            logger.error("Error uploading file %s to bucket %s: %s", file_path, target_bucket, e)
            raise RuntimeError(f"Storage upload failed: {e}") from e

    def download_file(self, file_path: str, bucket_name: Optional[str] = None) -> bytes:
        """
        Download binary content from Supabase Storage.
        """
        target_bucket = bucket_name or self.bucket_name
        client = self._get_client()
        try:
            data = client.storage.from_(target_bucket).download(file_path)
            return data
        except Exception as e:
            logger.error("Error downloading file %s from bucket %s: %s", file_path, target_bucket, e)
            raise RuntimeError(f"Storage download failed: {e}") from e

    def get_signed_url(
        self,
        file_path: str,
        expires_in: int = 3600,
        bucket_name: Optional[str] = None,
    ) -> str:
        """
        Generate a temporary time-limited signed URL for secure file download/viewing.
        """
        target_bucket = bucket_name or self.bucket_name
        client = self._get_client()
        try:
            result = client.storage.from_(target_bucket).create_signed_url(file_path, expires_in)
            if isinstance(result, dict) and "signedUrl" in result:
                return result["signedUrl"]
            elif hasattr(result, "get") and result.get("signedUrl"):
                return result.get("signedUrl")
            elif isinstance(result, str):
                return result
            return str(result)
        except Exception as e:
            logger.error("Error generating signed URL for %s: %s", file_path, e)
            raise RuntimeError(f"Signed URL creation failed: {e}") from e

    def delete_file(self, file_path: str, bucket_name: Optional[str] = None) -> bool:
        """
        Delete a file from Supabase Storage.
        """
        target_bucket = bucket_name or self.bucket_name
        client = self._get_client()
        try:
            client.storage.from_(target_bucket).remove([file_path])
            logger.info("Deleted file %s from bucket %s", file_path, target_bucket)
            return True
        except Exception as e:
            logger.error("Error deleting file %s from bucket %s: %s", file_path, target_bucket, e)
            return False

    def list_files(
        self,
        folder: str = "",
        bucket_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List files in a specific folder path within the bucket.
        """
        target_bucket = bucket_name or self.bucket_name
        client = self._get_client()
        try:
            items = client.storage.from_(target_bucket).list(path=folder, options={"limit": limit})
            result = []
            for item in items:
                if isinstance(item, dict):
                    result.append(item)
                else:
                    result.append({
                        "name": getattr(item, "name", str(item)),
                        "id": getattr(item, "id", None),
                        "created_at": getattr(item, "created_at", None),
                        "metadata": getattr(item, "metadata", {}),
                    })
            return result
        except Exception as e:
            logger.error("Error listing files in %s/%s: %s", target_bucket, folder, e)
            return []


storage_service = SupabaseStorageService()
