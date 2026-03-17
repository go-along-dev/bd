<<<<<<< HEAD
import time
import uuid
import logging
import json
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings


# ─── JSON Formatter ───────────────────────────
class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON for Cloud Logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "level":      record.levelname,
            "logger":     record.name,
            "message":    record.getMessage(),
        }
        # Include extra fields if attached
        for key in ("request_id", "user_id", "path", "method"):
            if hasattr(record, key):
                log_obj[key] = getattr(record, key)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


# ─── Configure Logging ────────────────────────
def configure_logging() -> None:
    """
    Set up structured JSON logging.
    DEBUG in development, INFO in production.
    Called once at app startup from main.py lifespan.
    """
    log_level = logging.DEBUG if settings.APP_ENV == "development" else logging.INFO

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add JSON handler
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.WARNING)


# ─── App Logger ───────────────────────────────
logger = logging.getLogger("goalong")


# ─── Tracing Middleware ───────────────────────
class TracingMiddleware(BaseHTTPMiddleware):
    """
    Outermost middleware — runs on every request.
    Generates request_id, times the request, logs structured JSON.
    GCP Cloud Logging picks up stdout JSON automatically.
    """

    async def dispatch(self, request: Request, call_next) -> Response:

        # 1. Generate or read request ID
        request_id = (
            request.headers.get("X-Request-ID")
            or str(uuid.uuid4())
        )
        request.state.request_id = request_id

        # 2. Start timer
        start_time = time.perf_counter()

        # 3. Process request
        response = await call_next(request)

        # 4. Calculate duration
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 5. Get user_id if available
        user_id = getattr(request.state, "user_id", None)

        # 6. Log structured request
        log_record = {
            "request_id":  request_id,
            "method":      request.method,
            "path":        request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "user_id":     str(user_id) if user_id else None,
            "timestamp":   datetime.now(timezone.utc).isoformat(),
        }

        # Choose log level based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_record))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_record))
        else:
            logger.info(json.dumps(log_record))

        # 7. Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
=======
# =============================================================================
# middleware/logging.py — Request/Response Logging & Tracing Middleware
# =============================================================================
# See: system-design/12-security-observability-slo.md §5 "Structured Logging"
# See: system-design/12-security-observability-slo.md §6 "Distributed Tracing"
#
# Structured JSON logging for Cloud Run → Cloud Logging integration.
#
# TODO: class TracingMiddleware(BaseHTTPMiddleware):
#       """
#       Outermost middleware. Runs on every request.
#
#       On request:
#       1. Generate request_id (UUID4) or read from X-Request-ID header
#       2. Attach to request.state.request_id
#       3. Start timer
#
#       On response:
#       4. Calculate duration_ms
#       5. Log structured JSON:
#          {
#              "request_id": "...",
#              "method": "GET",
#              "path": "/api/v1/rides",
#              "status_code": 200,
#              "duration_ms": 45,
#              "user_id": "..." (if available from request.state),
#              "timestamp": "ISO8601"
#          }
#       6. Add X-Request-ID to response headers
#
#       GCP Cloud Logging picks up stdout JSON automatically.
#       """
#
# TODO: Configure Python logging:
#       - Use structlog or stdlib logging with JSON formatter
#       - Log level from config: DEBUG in development, INFO in production
#       - Suppress noisy loggers (uvicorn.access, sqlalchemy.engine)
#
# Connects with:
#   → app/main.py (add as first middleware)
#   → app/config.py (APP_ENV determines log level)
#   → All services (import logger and use structured logging)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
