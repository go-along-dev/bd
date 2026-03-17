<<<<<<< HEAD
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db.postgres import engine
from app.db.mongo import connect_mongo, close_mongo
from app.services import osrm_service
from app.middleware.logging import TracingMiddleware, configure_logging
from app.middleware.auth import AuthMiddleware
from app.utils.exceptions import AppException, app_exception_handler
from app.admin.views import setup_admin
from app.routers import (
    auth, users, drivers,
    rides, bookings,
    wallet, chat, fare,
)


# ─── Lifespan ─────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await connect_mongo()
    print("✅ GoAlong API started")
    yield
    await close_mongo()
    await osrm_service.close_client()
    print("🔴 GoAlong API stopped")


# ─── App ──────────────────────────────────────
app = FastAPI(
    title       = "GoAlong API",
    description = "Intercity ride-sharing platform",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
    lifespan    = lifespan,
)

# ─── Middleware ───────────────────────────────
app.add_middleware(TracingMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.cors_origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ─── Exception Handlers ───────────────────────
app.add_exception_handler(AppException, app_exception_handler)

# ─── Admin Panel ──────────────────────────────
setup_admin(app, engine)

# ─── Routers ──────────────────────────────────
app.include_router(auth.router,     prefix="/api/v1")
app.include_router(users.router,    prefix="/api/v1")
app.include_router(drivers.router,  prefix="/api/v1")
app.include_router(rides.router,    prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(wallet.router,   prefix="/api/v1")
app.include_router(chat.router,     prefix="/api/v1")
app.include_router(fare.router,     prefix="/api/v1")

# ─── Health Check ─────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
=======
# =============================================================================
# main.py — FastAPI Application Entrypoint
# =============================================================================
# See: system-design/00-architecture.md §4 "Project Structure"
# See: system-design/12-security-observability-slo.md for middleware ordering
#
# This file is the single entrypoint. Uvicorn targets this: uvicorn app.main:app
#
# TODO: Initialize FastAPI app instance with metadata (title, version, docs_url)
# TODO: Use the `lifespan` context manager (NOT deprecated @app.on_event):
#       @asynccontextmanager
#       async def lifespan(app: FastAPI):
#           # --- Startup ---
#           engine = create_async_engine(settings.SUPABASE_DB_URL, ...)
#           await connect_mongo()
#           logger.info("GoAlong API started", env=settings.APP_ENV)
#           yield
#           # --- Shutdown ---
#           await dispose_engine()
#           await close_mongo()
#       app = FastAPI(lifespan=lifespan, ...)
#
# TODO: Register custom AppException handler:
#       @app.exception_handler(AppException)
#       async def app_exception_handler(request, exc):
#           return JSONResponse(
#               status_code=exc.status_code,
#               content={"detail": exc.detail, "code": exc.code}
#           )
#
# TODO: Register middleware in correct order:
#       1. TracingMiddleware (outermost — assigns request_id to every request)
#       2. SessionMiddleware (required by SQLAdmin, uses APP_SECRET_KEY)
#       3. CORSMiddleware (allow Flutter app origins from config.CORS_ORIGINS)
#       4. SlowAPI rate limiter (see 12-security-observability-slo.md §3)
# TODO: Include all routers under /api/v1 prefix:
#       - auth_router      → /api/v1/auth
#       - users_router     → /api/v1/users
#       - drivers_router   → /api/v1/drivers
#       - rides_router     → /api/v1/rides
#       - bookings_router  → /api/v1/bookings
#       - fare_router      → /api/v1/fare
#       - chat_router      → /api/v1/chat
#       - wallet_router    → /api/v1/wallet
# TODO: Mount SQLAdmin at /admin:
#       from app.admin.views import setup_admin
#       setup_admin(app, engine)
# TODO: Add /health endpoint (GET, no auth) returning {"status": "ok"}
#       Cloud Run uses this as liveness probe.
# TODO: Configure structured JSON logging via structlog
#       (see 12-security-observability-slo.md §5)
#
# Connects with:
#   → app/config.py (loads all env vars)
#   → app/routers/*.py (all route handlers)
#   → app/db/postgres.py (DB engine lifecycle)
#   → app/db/mongo.py (MongoDB client lifecycle)
#   → app/admin/views.py (SQLAdmin mount)
#   → app/middleware/*.py (middleware classes)
#   → app/utils/exceptions.py (AppException handler)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
