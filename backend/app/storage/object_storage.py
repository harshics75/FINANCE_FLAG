"""File storage abstraction. "local" writes/reads plain disk (fine when the backend
and worker share a filesystem, e.g. Docker Compose). "r2" writes/reads Cloudflare R2
(S3-compatible), needed when the backend and worker run as separate hosts with no
shared disk — the parsers (PyMuPDF/pdfplumber/openpyxl) all need a real local path,
so reading an R2-stored file downloads it to a temp file first."""
import os
import tempfile
import uuid
from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from app.config.settings import get_settings

settings = get_settings()


def _safe_filename(filename: str) -> str:
    """Strip any directory components so a crafted filename (e.g. '../../etc/x')
    can't escape the intended storage location."""
    return os.path.basename(filename) or "upload.bin"


@lru_cache
def _r2_client():
    import boto3
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint_url,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        region_name="auto",
    )


def save_bytes(data: bytes, filename: str) -> str:
    """Save uploaded file bytes. Returns a storage reference (local path or R2 key)
    to persist as Document.storage_path."""
    safe_name = _safe_filename(filename)
    if settings.storage_provider == "r2":
        key = f"documents/{uuid.uuid4().hex}_{safe_name}"
        _r2_client().put_object(Bucket=settings.r2_bucket_name, Key=key, Body=data)
        return key

    os.makedirs(settings.upload_dir, exist_ok=True)
    path = os.path.join(settings.upload_dir, safe_name)
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(path):  # simple versioned filenames
        path = f"{base}_v{n}{ext}"
        n += 1
    with open(path, "wb") as f:
        f.write(data)
    return path


@contextmanager
def local_path(storage_ref: str, name_hint: str = "", content: bytes | None = None) -> Iterator[str]:
    """Yield a real local filesystem path for a stored file: the file itself if
    storage_provider is "local"; a temp download if it's an R2 key; or the given
    `content` bytes (storage_provider="db", already loaded from the DB row) written
    to a temp file. `name_hint` (e.g. the original filename) is only used to pick the
    right temp-file extension when content is passed directly."""
    if content is not None:
        suffix = os.path.splitext(name_hint)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            yield tmp_path
        finally:
            os.unlink(tmp_path)
        return

    if settings.storage_provider != "r2":
        yield storage_ref
        return

    suffix = os.path.splitext(storage_ref)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
    try:
        _r2_client().download_file(settings.r2_bucket_name, storage_ref, tmp_path)
        yield tmp_path
    finally:
        os.unlink(tmp_path)
