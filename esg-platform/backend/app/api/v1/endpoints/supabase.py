"""
Supabase Integration Diagnostics & Status API Endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import settings
from app.core.supabase import check_supabase_connection
from app.db.session import get_db
from app.services.storage import storage_service

router = APIRouter()


@router.get("/status", response_model=Dict[str, Any], summary="Supabase Integration Status Check")
async def get_supabase_status(db: AsyncSession = Depends(get_db)):
    """
    Returns full diagnostic status for Supabase integration:
    - Supabase Client & API configuration
    - PostgreSQL database connectivity ping
    - Supabase Storage bucket access
    """
    connection_status = check_supabase_connection()
    
    db_healthy = False
    db_message = ""
    try:
        result = await db.execute(text("SELECT 1"))
        db_healthy = result.scalar() == 1
        db_message = "Database query executed successfully"
    except Exception as e:
        db_healthy = False
        db_message = f"Database query error: {str(e)}"

    return {
        "status": "healthy" if (connection_status.get("configured") and db_healthy) else "degraded",
        "supabase": connection_status,
        "database": {
            "connected": db_healthy,
            "message": db_message,
        },
        "config": {
            "url_configured": bool(settings.SUPABASE_URL),
            "storage_bucket": settings.STORAGE_BUCKET,
            "environment": settings.ENVIRONMENT,
        },
    }


@router.post("/ensure-bucket", summary="Ensure Storage Bucket Exists")
async def ensure_storage_bucket(bucket_name: str = settings.STORAGE_BUCKET):
    """
    Verifies or initializes a Supabase Storage bucket.
    """
    success = storage_service.ensure_bucket_exists(bucket_name=bucket_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify or create Supabase Storage bucket '{bucket_name}'.",
        )
    return {
        "success": True,
        "message": f"Storage bucket '{bucket_name}' verified.",
        "bucket": bucket_name,
    }
