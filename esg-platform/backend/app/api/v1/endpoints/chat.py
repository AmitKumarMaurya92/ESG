"""
AI Assistant endpoint.

Uses the real ESG AI assistant with RAG context retrieval from org data.
"""

import uuid
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.session import get_db
from app.ai.assistant import chat_with_assistant

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sources: list[str]


@router.post("/", response_model=ChatResponse,
             summary="Chat with the ESG AI Assistant",
             description="""
Ask questions about your organization's ESG data.

Examples:
- "Why did our Scope 2 emissions increase?"
- "What are our largest emission sources?"
- "Which compliance requirements are incomplete?"
- "Summarize our ESG performance."

The assistant uses only verified data from your organization. It does not fabricate facts.
""")
async def chat_with_esg_assistant(
    chat_in: ChatRequest,
    org_id: str = Depends(deps.get_current_organization),
    db: AsyncSession = Depends(get_db),
) -> Any:
    response, sources = await chat_with_assistant(
        db=db,
        organization_id=uuid.UUID(org_id),
        user_message=chat_in.message,
    )
    return {"response": response, "sources": sources}
