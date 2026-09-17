# ESG Intelligence & Carbon Accounting Platform

> AI-powered ESG intelligence and carbon accounting for modern enterprises.
> Scope 1, 2 & 3 GHG calculations · ESG scoring · Compliance mapping · Document AI · RAG ESG Assistant.

---

## Project Overview

The ESG Intelligence Platform centralises fragmented ESG operational data into one audit-ready repository.
It is built as a production-quality, scalable, multi-tenant SaaS application following a **37-phase** incremental build plan.

### Core Principle

> Use AI where AI helps. Use deterministic math where it matters.

```
Raw Data → Validation → Deterministic Calculation Engine → Verified DB → AI/RAG for explanation
```

The LLM **may** extract, classify, summarize, explain, and answer questions.
The LLM **must NOT** invent emission factors, calculations, or compliance requirements.

---

## Features (Full Platform — All Phases)

| Category | Capabilities |
|---|---|
| **Carbon** | Scope 1, 2, 3 · Emission factor DB (versioned) · Audit trails · Unit conversion |
| **ESG** | Configurable metrics · Weighted scoring engine · Trend analysis |
| **Documents** | PDF/OCR/CSV/Excel ingestion · AI extraction · Human review workflow |
| **Compliance** | GHG Protocol · GRI · BRSR · ESRS · Configurable frameworks |
| **AI** | RAG assistant · Anomaly detection · Document understanding |
| **Reporting** | PDF · Excel · CSV · Executive summaries |
| **Supplier Portal** | ESG questionnaires · Evidence collection · Status tracking |
| **Multi-tenancy** | Strict tenant isolation · RBAC · Supabase RLS |
| **API** | Versioned REST API · API keys · Rate limiting |
| **SaaS** | Plans (Free/Pro/Enterprise) · Feature flags · Usage tracking |

---

## Architecture

```
                React Frontend (Vite + Tailwind)
                         |
                      REST API
                         |
                      FastAPI
                         |
      ┌──────────────────┼──────────────────┐
      ↓                  ↓                  ↓
Carbon Engine       ESG Engine          AI Engine
      |                  |                  |
Scope 1/2/3        ESG Metrics        OCR/RAG/LLM
      |                  |                  |
      └──────────────────┼──────────────────┘
                         |
                      Supabase
                         |
      ┌──────────────────┼──────────────────┐
      ↓                  ↓                  ↓
  PostgreSQL          Storage             Auth
      |
   pgvector
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19 · Vite · Tailwind CSS v4 · React Router · TanStack React Query · Recharts · Lucide |
| **Backend** | Python 3.11 · FastAPI · Pydantic v2 · SQLAlchemy 2 · Alembic |
| **Database** | Supabase PostgreSQL · pgvector |
| **Auth** | Supabase Auth · JWT |
| **Storage** | Supabase Storage |
| **AI** | OpenAI / Gemini / Anthropic (pluggable) · Sentence Transformers |
| **OCR** | PyMuPDF · Tesseract · EasyOCR |
| **Workers** | Redis · Celery |
| **ML** | scikit-learn · pandas · NumPy |
| **Reporting** | ReportLab · openpyxl |

---

## Folder Structure

```
esg-platform/
│
├── frontend/                    # React + Vite frontend
│   ├── src/
│   │   ├── api/                 # Axios client
│   │   ├── components/          # Reusable UI components
│   │   ├── context/             # React context (Auth, etc.)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page-level components
│   │   ├── services/            # API service functions
│   │   └── utils/               # Helpers
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application factory
│   │   ├── api/v1/              # API routers and endpoints
│   │   ├── core/                # Config, logging, exceptions
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic layer
│   │   ├── repositories/        # Data access layer
│   │   ├── db/                  # Database session management
│   │   ├── ai/                  # LLM provider abstraction + RAG
│   │   ├── carbon/              # Deterministic GHG calculation engine
│   │   ├── compliance/          # Framework compliance engine
│   │   ├── tasks/               # Celery background tasks
│   │   └── utils/               # Shared helpers
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # pytest test suite
│   ├── requirements.txt
│   └── .env.example
│
├── ml/                          # ML model training and inference
├── workers/                     # Celery worker configuration
├── data/
│   ├── emission_factors/        # Authoritative EF datasets
│   ├── regulatory/              # Framework documents for RAG
│   └── sample/                  # Synthetic sample data
│
├── docker/                      # Dockerfiles
│   ├── backend/Dockerfile
│   └── frontend/Dockerfile
│
├── docs/                        # Additional documentation
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Settings → API** and copy:
   - Project URL → `SUPABASE_URL`
   - Anon key → `SUPABASE_ANON_KEY`
   - Service role key → `SUPABASE_SERVICE_ROLE_KEY` (**backend only, never frontend**)
3. Go to **Settings → Database** and copy the connection string → `DATABASE_URL`
4. Enable the `pgvector` extension: SQL Editor → `CREATE EXTENSION IF NOT EXISTS vector;`

---

## Environment Variables

### Backend (`backend/.env`)

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase credentials
```

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin key — backend only, never exposed to frontend |
| `DATABASE_URL` | PostgreSQL connection string (asyncpg format) |
| `JWT_SECRET` | Random secret for JWT signing |
| `LLM_API_KEY` | OpenAI / Gemini / Anthropic API key |
| `REDIS_URL` | Redis connection URL |

### Frontend (`frontend/.env.local`)

```bash
cp frontend/.env.example frontend/.env.local
# Edit with your Supabase anon key only
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- Redis (for background workers — optional in Phase 1)

### Backend

```powershell
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the development server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend

# Install dependencies
npm install

# Copy and configure environment
cp .env.example .env.local
# Edit .env.local

# Run the development server
npm run dev
```

### Test URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Health check | http://localhost:8000/health |
| API v1 health | http://localhost:8000/api/v1/health |
| OpenAPI docs | http://localhost:8000/api/v1/docs |

---

## Testing

```powershell
cd backend

# Activate virtual environment first
.venv\Scripts\activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_health.py -v
```

---

## Docker

```powershell
# Copy environment files first
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Build and start all services
docker compose up --build

# Run in background
docker compose up -d --build

# Stop
docker compose down
```

---

## API Documentation

- **Interactive docs (Swagger UI):** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

### Current Endpoints (Phase 1)

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Root health check (load balancer probe) |
| `GET` | `/api/v1/health` | Full health response with version and uptime |

---

## Build Phases

| Phase | Feature |
|---|---|
| **1** | ✅ Project foundation |
| **2** | ✅ Supabase integration (current) |
| **3** | Authentication |
| **4** | Multi-tenancy & RBAC |
| **5** | React frontend foundation |
| **6** | Organization onboarding |
| **7** | Facility management |
| **8** | Document upload |
| **9** | CSV/Excel ingestion |
| **10** | OCR / Document extraction |
| **11** | Emission factor database |
| **12** | Carbon calculation engine |
| **13** | Scope 1 |
| **14** | Scope 2 |
| **15** | Scope 3 |
| **16–17** | ESG metrics & scoring |
| **18–19** | Anomaly detection & risk engine |
| **20–21** | RAG infrastructure & AI assistant |
| **22–23** | Compliance engine & dashboards |
| **24** | Carbon & ESG dashboards |
| **25** | Supplier portal |
| **26** | Reporting engine |
| **27** | Audit logging |
| **28** | Public API |
| **29–30** | Usage tracking & subscriptions |
| **31** | Notifications |
| **32** | Admin dashboard |
| **33** | Background workers |
| **34** | Security hardening |
| **35** | Testing |
| **36** | Docker |
| **37** | Production deployment |

---

## Demo Workflow (End-to-End)

1. Register → create organization → complete onboarding
2. Add facility
3. Upload electricity invoice (PDF)
4. OCR extracts consumption data
5. Human reviews and approves extracted data
6. System selects correct emission factor (versioned)
7. Scope 2 CO₂e is calculated deterministically
8. ESG metrics and score update
9. Compliance requirements are checked
10. Dashboard shows updated data
11. AI assistant explains the result using source evidence
12. PDF report is generated with full audit trail

---

## Security

- **Supabase service role key** — backend only, never exposed to frontend
- **Tenant isolation** — every query is scoped to `organization_id`; cross-tenant access is blocked at API and RLS layers
- **RBAC** — 7 roles (SUPER_ADMIN, ORGANIZATION_ADMIN, SUSTAINABILITY_MANAGER, COMPLIANCE_OFFICER, AUDITOR, SUPPLIER, EMPLOYEE)
- **Structured error responses** — internal stack traces are never returned to clients
- **Audit logging** — every important action is recorded

---

## License

Proprietary — All rights reserved.
