"""Upload validation: type, size, basic integrity."""
from fastapi import HTTPException, UploadFile

ALLOWED = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-excel": ".xls",
}
MAX_BYTES = 50 * 1024 * 1024  # 50 MB


async def validate_upload(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED:
        raise HTTPException(415, f"Unsupported file type: {file.content_type}. Upload PDF or Excel.")
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(400, "Empty file.")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File exceeds 50 MB limit.")
    if file.content_type == "application/pdf" and not data[:5] == b"%PDF-":
        raise HTTPException(400, "File is not a valid PDF.")
    return data


def classify_doc_type(filename: str) -> str:
    f = filename.lower()
    rules = [
        ("annual", "annual_report"), ("quarter", "quarterly_report"),
        ("balance", "balance_sheet"), ("profit", "pnl"), ("p&l", "pnl"), ("pnl", "pnl"),
        ("loss", "pnl"), ("cash", "cash_flow"), ("audit", "audit_report"),
        ("mis", "monthly_mis"), ("monthly", "monthly_mis"), ("budget", "budget"),
        ("forecast", "forecast"),
    ]
    for key, doc_type in rules:
        if key in f:
            return doc_type
    return "excel" if f.endswith((".xlsx", ".xls")) else "unknown"
