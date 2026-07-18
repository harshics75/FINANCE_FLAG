# AI Financial Intelligence & Executive Dashboard

Enterprise-grade AI-powered financial analysis platform. Upload financial documents (Annual Reports, Balance Sheets, P&L, Cash Flow, Audit Reports, Monthly MIS), and the system extracts, embeds, analyzes, and generates an executive dashboard with AI-powered insights, risk detection, and recommendations.

## Architecture

- **Frontend:** React 18 + TypeScript + Vite + Tailwind + ShadCN-style components + Recharts + React Query + Framer Motion
- **Backend:** FastAPI + SQLAlchemy + Pydantic v2 + Celery + Redis + PostgreSQL
- **AI:** Local Ollama (`mistral:7b-instruct-q4_0` + `nomic-embed-text`, free, no signup) **or** Azure OpenAI (GPT-4o + text-embedding-3-large) — switchable via `LLM_PROVIDER` — LangChain + LangGraph + FAISS (Azure AI Search fallback) + PyMuPDF + pdfplumber + Tesseract OCR (Azure Document Intelligence fallback)
- **Auth:** OAuth2 password flow, JWT access/refresh tokens, RBAC (admin, finance_manager, auditor)
- **Deploy:** Docker, Docker Compose, Azure App Service + ACR, GitHub Actions CI/CD

## Quick start (local)

```bash
cp .env.example .env
docker compose up --build
```

By default `LLM_PROVIDER=ollama` — install [Ollama](https://ollama.com), then pull the two models
the backend expects before starting the stack:

```bash
ollama pull mistral:7b-instruct-q4_0
ollama pull nomic-embed-text
```

To use Azure OpenAI instead, set `LLM_PROVIDER=azure` in `.env` and fill in the `AZURE_OPENAI_*` keys.

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

Login → Dashboard → Upload → Validation → OCR/Text extraction → Table extraction → Chunking → Embeddings →
Vector store → Line-item extraction (PDF tables + Excel rows) → KPI engine → Metadata (PostgreSQL) →
LangGraph agent pipeline (Financial Analyst → Risk Detection → Market Comparison → Executive Summary →
Recommendations → Operational Highlights from monthly MIS) → Interactive dashboard + Chat with reports (RAG).

See [docs/architecture.md](docs/architecture.md) for a diagram of the container topology, the upload/processing
workflow, and the full 8-node agent pipeline.

## Repository layout

```
backend/app/
  api/routes/     REST endpoints (auth, documents, analysis, dashboard, chat, export)
  agents/         LangGraph agents + workflow graph (8 nodes, see docs/architecture.md)
  rag/            RAG pipeline (retriever, chunking, citation)
  embeddings/     Ollama/Azure OpenAI embeddings + vector store adapters
  parser/         PDF/Excel parsing, OCR, table extraction, line_items.py (shared line-item heuristic)
  analytics/      Deterministic financial KPI engine
  models/         SQLAlchemy ORM models
  schemas/        Pydantic request/response schemas
  repositories/   Data access layer
  auth/           JWT, OAuth2, RBAC
  middleware/     Logging, request ID, error handling
frontend/src/
  pages/          Executive Overview, Financial Performance, Cash Flow, Working Capital,
                  AI Insights, Operational Highlights, Document Explorer, Audit Findings,
                  Chat, Upload
  components/     KPI cards, charts, tables, shell
```

## Documentation

- [Architecture & workflow](docs/architecture.md) — container topology, upload/processing pipeline, 8-node agent pipeline
- [Azure deployment guide](docs/azure-deployment.md)
- [API documentation](docs/api.md)
- Interactive API docs auto-generated at `/docs` and `/redoc`

## Testing

```bash
cd backend && pytest
cd frontend && npm test
```
