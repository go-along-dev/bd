<<<<<<< HEAD
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt

from app.db.postgres import AsyncSessionLocal
from app.config import settings

security = HTTPBearer()


# ─── DB Session ───────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Pagination ───────────────────────────────
def get_pagination(page: int = 1, per_page: int = 20):
    if page < 1:
        page = 1
    if per_page > 100:
        per_page = 100
    offset = (page - 1) * per_page
    return {"page": page, "per_page": per_page, "offset": offset}


# ─── Current User ─────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            leeway=30,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    supabase_uid = payload.get("sub")
    if not supabase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Find or create user on first login
    result = await db.execute(
        select(User).where(User.supabase_uid == supabase_uid)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            supabase_uid=supabase_uid,
            phone=payload.get("phone"),
            email=payload.get("email"),
            role="passenger",
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated"
        )

    return user


# ─── Role Guards ──────────────────────────────
async def require_driver(current_user=Depends(get_current_user)):
    if current_user.role not in ("driver", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver access required"
        )
    return current_user


async def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
=======
# =============================================================================
# dependencies.py — Shared FastAPI Dependencies
# =============================================================================
# See: system-design/01-auth.md for JWT verification flow
# See: system-design/00-architecture.md §8 "Things To Note" — RLS is OFF,
#      all access control is handled here in FastAPI.
#
# FastAPI Depends() functions used across multiple routers.
#
# TODO: get_db() → AsyncGenerator[AsyncSession, None]
#       - Yields an async SQLAlchemy session from the session factory (db/postgres.py)
#       - Must use `async with` and yield pattern for proper cleanup
#       - Every router endpoint that touches PostgreSQL depends on this
#
# TODO: get_mongo() → AsyncIOMotorDatabase
#       - Returns the Motor database instance from db/mongo.py
#       - Used only by chat endpoints
#
# TODO: get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)) → User
#       - Extracts Bearer token from Authorization header
#       - Verifies JWT signature using Supabase JWT secret (from config)
#       - Decodes payload, extracts supabase_uid from 'sub' claim
#       - Queries users table by supabase_uid
#       - Returns User ORM object (or raises 401 if invalid/expired)
#       - This is THE authentication gate for all protected endpoints
#
# TODO: require_role(allowed_roles: list[str]) → Callable
#       - Returns a dependency that checks current_user.role against allowed_roles
#       - Raises 403 Forbidden if role not in list
#       - Usage: Depends(require_role(["driver", "admin"]))
#
# TODO: get_pagination(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100)) → dict
#       - Returns {"offset": (page - 1) * per_page, "limit": per_page}
#       - Used by all list endpoints via Depends(get_pagination)
#       - NOTE: No separate PaginationParams schema needed — FastAPI Query() handles validation
#
# Connects with:
#   → app/db/postgres.py (get_db uses async_session_factory)
#   → app/db/mongo.py (get_mongo uses global db reference)
#   → app/config.py (JWT secret for token verification)
#   → app/models/user.py (User model for DB lookup)
#   → app/routers/*.py (every router imports these deps)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
