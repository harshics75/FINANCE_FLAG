# Architecture & Workflow

## System architecture

Five containers behind one entry point. The browser only ever talks to `nginx:5173`, which serves
the built SPA and reverse-proxies `/api/*` to the backend. Heavy work (parsing, embedding, the agent
pipeline) runs on the Celery worker, never inline on a request.

```mermaid
flowchart TD
  B["Browser<br/>React 18 SPA"]
  N["nginx — :5173<br/>static assets + /api reverse proxy"]
  F["FastAPI backend — :8000<br/>REST API · JWT auth · RBAC"]
  W["Celery worker<br/>document + analysis pipeline"]
  R[("Redis<br/>task broker")]
  P[("PostgreSQL<br/>users · documents · chunks<br/>metrics · analysis_results · dashboard_data")]
  V[("FAISS index<br/>(or Azure AI Search)<br/>uploads volume")]
  L{{"Ollama : 11434<br/>(or Azure OpenAI)<br/>chat + embeddings"}}

  B -->|HTTPS| N
  N -->|"/api/v1/*"| F
  F --> P
  F -->|enqueue task| R
  R -->|deliver task| W
  W --> P
  W --> V
  F --> V
  F -->|LLM calls| L
  W -->|LLM calls| L
```

## Upload → processing workflow

Everything from `POST /documents/upload` to a searchable, KPI-bearing document. This runs entirely
on the worker, off the request thread — the endpoint returns immediately with `status: uploaded`.

```mermaid
flowchart TD
  A["POST /documents/upload<br/>file + fiscal_period"] --> B{"validate_upload<br/>MIME · ≤50MB · magic bytes"}
  B -->|reject| B1["415 / 400 / 413"]
  B -->|ok| C["save_upload → disk<br/>Document row, status = uploaded"]
  C --> D["process_document_task.delay()<br/>status = processing"]
  D --> E{"file type"}
  E -->|.pdf| F1["parse_pdf<br/>text + tables, OCR if scanned"]
  E -->|.xlsx / .xls| F2["parse_excel<br/>sheet → markdown + rows"]
  F1 --> G["chunk_text / chunk_table"]
  F2 --> G
  F1 --> H["extract_line_items<br/>(PDF tables)"]
  F2 --> H2["extract_line_items<br/>(Excel rows)"]
  G --> I["embed_texts → vector_store.upsert<br/>Chunk + Embedding rows"]
  H --> J{"line_items and<br/>fiscal_period set?"}
  H2 --> J
  J -->|yes| K["match_line_items<br/>→ FinancialMetric rows"]
  J -->|no| SK["skipped — no period tagged"]
  I --> M{"exception raised?"}
  K --> M
  SK --> M
  M -->|no| Done["status = embedded"]
  M -->|yes| O["status = failed<br/>error message stored"]
```

> **Why metrics can silently end up empty:** step `J` only persists `FinancialMetric` rows when a
> fiscal period was set at upload time. A document with no period still reaches `embedded`
> successfully — chat/RAG works — but contributes nothing to the KPI engine.

## AI analysis pipeline

Triggered by `POST /analysis/run`. A single LangGraph — 8 nodes, strictly sequential, each one
reading and extending a shared state object. Two nodes are pure retrieval (no LLM call); six are
agents that call the model and return structured JSON.

```mermaid
flowchart TD
  S["POST /analysis/run"] --> T["compute_kpis per period<br/>deterministic KPI engine"]
  T --> N1["① retrieve_context<br/>RAG search, k=10"]
  N1 --> N2["② financial_analyst<br/>margins · growth · cash-flow narrative"]
  N2 --> N3["③ risk_detection<br/>risk_score + categorized risks"]
  N3 --> N4["④ market_comparison<br/>vs. industry benchmarks"]
  N4 --> N5["⑤ executive_summary<br/>health score · green/red flags · insights"]
  N5 --> N6["⑥ recommendation<br/>prioritized actions"]
  N6 --> N7["⑦ retrieve_mis_context<br/>RAG search, doc_type=monthly_mis"]
  N7 --> N8["⑧ operational_highlights<br/>order book · projects · production ·<br/>legal/compliance · exceptional events"]
  N8 --> U["_materialize_dashboards"]
  U --> D1["executive"]
  U --> D2["performance"]
  U --> D3["cash_flow"]
  U --> D4["working_capital"]
  U --> D5["insights"]
  U --> D6["audit"]
  U --> D7["operational"]
  D1 & D2 & D3 & D4 & D5 & D6 & D7 --> DB[("dashboard_data")]
  DB --> G["GET /dashboard/{page}"]
```

A seventh agent runs outside this graph: the **Chat agent** (`chat_service.py`) is a single-shot
retrieve → answer step that fires per chat message on `POST /chat`, independent of the
"Run analysis" pipeline above.

## Stack reference

| Layer | Components |
|---|---|
| Frontend | React 18 + TypeScript + Vite, Tailwind, Recharts, React Query, Framer Motion — built static, served by nginx |
| Backend | FastAPI + SQLAlchemy + Pydantic v2, JWT / OAuth2 password flow, RBAC (admin · finance_manager · auditor) |
| Async | Celery worker + Redis broker — document processing and the analysis pipeline never block a request |
| AI / LLM | LangChain + LangGraph orchestration; local Ollama (mistral 7B-instruct + nomic-embed-text) or Azure OpenAI (GPT-4o + text-embedding-3-large), switched by `LLM_PROVIDER` |
| Retrieval | FAISS local vector index (Azure AI Search fallback), filterable by `doc_type` for scoped context |
| Parsing | PyMuPDF + pdfplumber for PDFs, pandas/openpyxl for Excel, Tesseract OCR fallback (Azure Document Intelligence alt) |
| Data | PostgreSQL — documents, chunks, embeddings, financial_metrics, analysis_results, dashboard_data, chat_history |
| Deploy | Docker Compose — db, redis, backend, worker, frontend containers on one bridge network |
