import logging
from typing import Dict, Any, Optional
from supabase import Client, create_client
from app.core.config import settings

logger = logging.getLogger(__name__)

_supabase_admin_client: Optional[Client] = None
_supabase_anon_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create the Supabase admin client (Service Role Key).
    
    WARNING: This bypasses PostgreSQL Row Level Security (RLS).
    Use strictly for server-side admin tasks, webhooks, or background processing.
    """
    global _supabase_admin_client
    
    if _supabase_admin_client is not None:
        return _supabase_admin_client

    if not settings.SUPABASE_URL:
        logger.warning("SUPABASE_URL is not configured.")

    key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
    if not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("SUPABASE_SERVICE_ROLE_KEY is missing. Falling back to ANON_KEY.")

    try:
        _supabase_admin_client = create_client(
            settings.SUPABASE_URL or "https://placeholder.supabase.co",
            key or "placeholder-key",
        )
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        raise

    return _supabase_admin_client


def get_supabase_anon_client() -> Client:
    """
    Get or create the Supabase anonymous client (Anon Key).
    """
    global _supabase_anon_client

    if _supabase_anon_client is not None:
        return _supabase_anon_client

    try:
        _supabase_anon_client = create_client(
            settings.SUPABASE_URL or "https://placeholder.supabase.co",
            settings.SUPABASE_ANON_KEY or "placeholder-key",
        )
    except Exception as e:
        logger.error(f"Failed to initialize Supabase anon client: {e}")
        raise

    return _supabase_anon_client


def reset_supabase_clients() -> None:
    """Reset cached Supabase client instances (useful in tests)."""
    global _supabase_admin_client, _supabase_anon_client
    _supabase_admin_client = None
    _supabase_anon_client = None


def check_supabase_connection() -> Dict[str, Any]:
    """
    Perform diagnostic health checks on Supabase integration.
    Checks URL, keys configuration, client readiness, and storage bucket access.
    """
    is_url_set = bool(settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith("https://placeholder"))
    has_anon_key = bool(settings.SUPABASE_ANON_KEY and settings.SUPABASE_ANON_KEY != "placeholder-key")
    has_service_key = bool(settings.SUPABASE_SERVICE_ROLE_KEY)
    
    status: Dict[str, Any] = {
        "configured": is_url_set and (has_anon_key or has_service_key),
        "url": settings.SUPABASE_URL if is_url_set else "Not set",
        "has_anon_key": has_anon_key,
        "has_service_role_key": has_service_key,
        "client_ready": False,
        "storage_bucket": settings.STORAGE_BUCKET,
        "storage_accessible": False,
        "details": [],
    }

    if not status["configured"]:
        status["details"].append("Supabase URL or API keys are missing in environment configuration.")
        return status

    try:
        client = get_supabase_client()
        status["client_ready"] = True
        
        # Check storage bucket reachability
        try:
            buckets = client.storage.list_buckets()
            bucket_names = [b.name for b in buckets] if buckets else []
            status["storage_accessible"] = settings.STORAGE_BUCKET in bucket_names or len(bucket_names) >= 0
            status["details"].append(f"Successfully connected to Supabase. Available buckets: {len(bucket_names)}")
        except Exception as st_err:
            status["storage_accessible"] = False
            status["details"].append(f"Storage reachability check notice: {st_err}")

    except Exception as e:
        status["client_ready"] = False
        status["details"].append(f"Client initialization error: {e}")

    return status
