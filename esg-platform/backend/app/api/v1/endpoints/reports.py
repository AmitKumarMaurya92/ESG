import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.report import Report
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import asyncio

router = APIRouter()

class ReportCreate(BaseModel):
    title: str
    report_type: str
    period: str
    format: str = "PDF"

class ReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    report_type: str
    period: str
    format: str
    status: str
    storage_path: str
    created_at: datetime
    model_config = {"from_attributes": True}

async def generate_pdf_report_task(report_id: uuid.UUID, org_id: uuid.UUID, db_session: AsyncSession):
    """Background task to generate a PDF report."""
    # In a real scenario, this would gather data and use ReportLab or WeasyPrint to generate a PDF.
    # For now, we simulate processing time and then update status.
    await asyncio.sleep(5) # Simulate PDF generation
    
    # Update the report status to COMPLETED
    stmt = select(Report).where(Report.id == report_id)
    result = await db_session.execute(stmt)
    report = result.scalars().first()
    if report:
        report.status = "COMPLETED"
        report.storage_path = f"{org_id}/reports/{report_id}.pdf"
        db_session.add(report)
        await db_session.commit()

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_in: ReportCreate,
    background_tasks: BackgroundTasks,
    org_id: str = Depends(deps.get_current_organization),
    current_user: Any = Depends(deps.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Request generation of a new ESG Report."""
    org_uuid = uuid.UUID(org_id)
    new_report = Report(
        **report_in.model_dump(),
        organization_id=org_uuid,
        generated_by=current_user.id,
        status="GENERATING",
        storage_path="pending..."
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    
    # Dispatch background task for PDF generation
    # NOTE: Since db sessions can't be easily shared across threads/tasks in async safely,
    # usually you'd dispatch to Celery. For demo purposes we'll pass the session, but
    # in production this should be a separate worker picking up the task.
    # We will simulate it using a basic async task for now.
    
    return new_report

@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all reports for the organization."""
    stmt = select(Report).where(Report.organization_id == uuid.UUID(org_id)).order_by(Report.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()
