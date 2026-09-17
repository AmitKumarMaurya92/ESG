import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.document import Document
from app.models.user import UserProfile
from app.services.storage import SupabaseStorageService
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import asyncio

router = APIRouter()

async def simulate_ocr_processing(doc_id: uuid.UUID, db_session: AsyncSession):
    """Simulates AI OCR extraction pipeline."""
    await asyncio.sleep(2)
    # Update to PROCESSING
    stmt = select(Document).where(Document.id == doc_id)
    doc = (await db_session.execute(stmt)).scalars().first()
    if doc:
        doc.processing_status = "PROCESSING"
        db_session.add(doc)
        await db_session.commit()
        
    await asyncio.sleep(3)
    # Update to EXTRACTED
    doc = (await db_session.execute(stmt)).scalars().first()
    if doc:
        doc.processing_status = "EXTRACTED"
        db_session.add(doc)
        await db_session.commit()

class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    mime_type: str
    size_bytes: int
    document_type: Optional[str]
    processing_status: str
    created_at: datetime

    model_config = {"from_attributes": True}

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    org_id: str = Depends(deps.get_current_organization),
    current_user: UserProfile = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Upload a document to storage and create a DB record."""
    # Basic validation
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file")
        
    # Generate unique path
    doc_id = uuid.uuid4()
    path = f"{org_id}/{doc_id}_{file.filename}"
    
    # Upload to Supabase Storage
    storage_service = SupabaseStorageService()
    try:
        storage_service.upload_file(
            file_bytes=file_bytes,
            path=path,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

    # Save to DB
    new_doc = Document(
        id=doc_id,
        organization_id=uuid.UUID(org_id),
        uploader_id=current_user.id,
        filename=file.filename,
        mime_type=file.content_type,
        size_bytes=len(file_bytes),
        storage_path=path,
        processing_status="UPLOADED"
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    # Dispatch simulated OCR processing task
    # Note: Using db session in background task is unsafe in production, we do this for demo simplicity
    background_tasks.add_task(simulate_ocr_processing, doc_id, db)
    
    return new_doc

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List documents for the organization."""
    stmt = select(Document).where(Document.organization_id == uuid.UUID(org_id)).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a document."""
    stmt = select(Document).where(
        Document.id == document_id,
        Document.organization_id == uuid.UUID(org_id)
    )
    result = await db.execute(stmt)
    doc = result.scalars().first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Remove from storage
    storage_service = SupabaseStorageService()
    try:
        storage_service.delete_file(doc.storage_path)
    except Exception as e:
        pass # If file is already gone, just delete DB record

    await db.delete(doc)
    await db.commit()
