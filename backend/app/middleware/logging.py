import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID, log method/path/status/duration."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled error request_id=%s %s %s", request_id, request.method, request.url.path)
            raise
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["x-request-id"] = request_id
        logger.info("%s %s %s %.1fms request_id=%s", request.method, request.url.path,
                    response.status_code, duration_ms, request_id)
        return response
