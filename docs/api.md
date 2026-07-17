# API Documentation

Base URL: `/api/v1` · Auth: `Authorization: Bearer <access_token>` · Interactive docs at `/docs`.

## Authentication
| Method | Path | Role | Description |
|---|---|---|---|
| POST | /auth/login | — | OAuth2 password form (`username`, `password`) → access + refresh tokens |
| POST | /auth/refresh | — | Exchange refresh token for a new pair |
| POST | /auth/register | admin | Create a user (roles: admin, finance_manager, auditor) |
| GET | /auth/me | any | Current user profile |

## Documents
| POST | /documents/upload | finance_manager+ | Multipart PDF/Excel + `fiscal_period`; async processing (validate → OCR → extract → chunk → embed) |
| GET | /documents | any | List documents with status |
| GET | /documents/{id} | any | Document detail |
| GET | /documents/{id}/chunks | any | Extracted text/table chunks |

## Analysis
| POST | /analysis/run | finance_manager+ | Run KPI engine + LangGraph agent pipeline (async) |
| GET | /analysis/runs/{run_id} | any | All agent results for a run |
| GET | /analysis/agents/{agent}/latest | any | Latest result for one agent |
| GET | /analysis/metrics | any | All computed financial metrics |

Agents: `financial_analyst`, `risk_detection`, `market_comparison`, `executive_summary`, `recommendation`.

## Dashboard
| GET | /dashboard/{page} | any | Pages: `executive`, `performance`, `cash_flow`, `working_capital`, `insights`, `audit` |

## Chat
| POST | /chat | any | `{session_id?, message}` → grounded answer + citations |
| GET | /chat/sessions/{session_id} | any | Chat history |

## Export
| GET | /export/pdf | any | Executive report PDF |
| GET | /export/excel | any | Financial metrics workbook |

## Error format
Errors return `{"detail": "message"}` with standard HTTP codes (401 unauthenticated, 403 forbidden, 404 not found, 413 too large, 415 unsupported type). Every response carries an `x-request-id` header for log correlation.
