# AI Financial Intelligence & Executive Dashboard

Enterprise-grade AI-powered financial analysis platform. Upload financial documents (Annual Reports, Balance Sheets, P&L, Cash Flow, Audit Reports, Monthly MIS), and the system extracts, embeds, analyzes, and generates an executive dashboard with AI-powered insights, risk detection, and recommendations.

## Architecture

- **Frontend:** React 18 + TypeScript + Vite + Tailwind + ShadCN-style components + Recharts + React Query + Framer Motion
- **Backend:** FastAPI + SQLAlchemy + Pydantic v2 + Celery + Redis + PostgreSQL
- **AI:** Azure OpenAI (GPT-4o / GPT-4.1) + text-embedding-3-large + LangChain + LangGraph + Azure AI Search (FAISS fallback) + PyMuPDF + pdfplumber + Azure Document Intelligence (Tesseract fallback)
- **Auth:** OAuth2 password flow, JWT access/refresh tokens, RBAC (admin, finance_manager, auditor)
- **Deploy:** Docker, Docker Compose, Azure App Service + ACR, GitHub Actions CI/CD

## Quick start (local)

```bash
cp .env.example .env          # fill in Azure OpenAI keys
docker compose up --build
```

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs
- Default admin (dev seed): admin@example.com / ChangeMe123!

## Without Docker

Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
celery -A app.services.worker.celery_app worker -l info   # separate shell
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Application flow

Login → Dashboard → Upload → Validation → OCR/Text extraction → Table extraction → Chunking → Embeddings → Vector store → Metadata (PostgreSQL) → LangGraph agent pipeline (Financial Analyst → Risk Detection → Market Comparison → Executive Summary → Recommendations) → KPI engine → Interactive dashboard + Chat with reports (RAG).

## Repository layout

```
backend/app/
  api/routes/     REST endpoints (auth, documents, analysis, dashboard, chat, export)
  agents/         LangGraph agents + workflow graph
  rag/            RAG pipeline (retriever, chunking, citation)
  embeddings/     Azure OpenAI embeddings + vector store adapters
  parser/         PDF/Excel parsing, OCR, table extraction
  analytics/      Deterministic financial KPI engine
  models/         SQLAlchemy ORM models
  schemas/        Pydantic request/response schemas
  repositories/   Data access layer
  auth/           JWT, OAuth2, RBAC
  middleware/     Logging, request ID, error handling
frontend/src/
  pages/          Executive Overview, Financial Performance, Cash Flow,
                  Working Capital, AI Insights, Document Explorer, Audit Findings, Chat
  components/     KPI cards, charts, tables, shell
```

## Documentation

- [Azure deployment guide](docs/azure-deployment.md)
- [API documentation](docs/api.md)
- Interactive API docs auto-generated at `/docs` and `/redoc`

## Testing

```bash
cd backend && pytest
cd frontend && npm test
```
