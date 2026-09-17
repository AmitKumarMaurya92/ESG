"""
API v1 router aggregator.

All feature routers are registered here and mounted under /api/v1
in main.py.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, supabase, auth, users, organizations, facilities, documents, emissions, analytics, reports, suppliers, compliance, chat, esg, audit_logs

api_router = APIRouter()

# ── Auth ──────────────────────────────────────────────────────────────────────
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# ── Health ────────────────────────────────────────────────────────────────────
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

# ── Supabase ──────────────────────────────────────────────────────────────────
api_router.include_router(
    supabase.router,
    prefix="/supabase",
    tags=["Supabase Integration"],
)

# ── Users ─────────────────────────────────────────────────────────────────────
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

# ── Organizations ─────────────────────────────────────────────────────────────
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"],
)

# ── Facilities ────────────────────────────────────────────────────────────────
api_router.include_router(
    facilities.router,
    prefix="/facilities",
    tags=["Facilities"],
)

# ── Documents ─────────────────────────────────────────────────────────────────
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

# ── Emissions ─────────────────────────────────────────────────────────────────
api_router.include_router(
    emissions.router,
    prefix="/emissions",
    tags=["Emissions"],
)

# ── Analytics ─────────────────────────────────────────────────────────────────
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
)

# ── Reports ───────────────────────────────────────────────────────────────────
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"],
)

# ── Suppliers ─────────────────────────────────────────────────────────────────
api_router.include_router(
    suppliers.router,
    prefix="/suppliers",
    tags=["Suppliers"],
)

# ── Compliance ────────────────────────────────────────────────────────────────
api_router.include_router(
    compliance.router,
    prefix="/compliance",
    tags=["Compliance"],
)

# ── AI Assistant ──────────────────────────────────────────────────────────────
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["AI Assistant"],
)

# ── ESG Metrics & Scoring ─────────────────────────────────────────────────────
api_router.include_router(
    esg.router,
    prefix="/esg",
    tags=["ESG Metrics & Scoring"],
)

# ── Audit Logs ────────────────────────────────────────────────────────────────
api_router.include_router(
    audit_logs.router,
    prefix="/audit-logs",
    tags=["Audit Logs"],
)
