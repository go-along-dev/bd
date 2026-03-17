<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserUpdateRequest


# ─── Get User By ID ───────────────────────────
async def get_user_by_id(
    db: AsyncSession,
    user_id: UUID,
) -> User | None:
    """Fetch user by primary key. Used for public profile views."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


# ─── Update Profile ───────────────────────────
async def update_profile(
    db: AsyncSession,
    user: User,
    data: UserUpdateRequest,
) -> User:
    """
    Partial update — only non-None fields are updated.
    Phone cannot be changed here (managed by Supabase Auth).
    """
    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        user.email = data.email
    if data.profile_photo is not None:
        user.profile_photo = data.profile_photo

    await db.commit()
    await db.refresh(user)
    return user
=======
# =============================================================================
# services/user_service.py — User Profile Service
# =============================================================================
# See: system-design/02-user-driver.md §1 "User Profile"
# See: system-design/10-api-contracts.md §3 "User Endpoints"
#
# TODO: async def get_user_by_id(db: AsyncSession, user_id: UUID) → User | None:
#       """Fetch user by primary key. Used for public profile views."""
#
# TODO: async def update_profile(db: AsyncSession, user: User, data: UserUpdateRequest) → User:
#       """
#       Partial update — only non-None fields are updated.
#       Phone cannot be changed here (managed by Supabase Auth).
#       If profile_photo URL changes, the old photo should ideally be deleted
#       from Supabase Storage (via storage_service) — but OK to skip for MVP.
#       """
#
# Connects with:
#   → app/routers/users.py (calls get_user_by_id, update_profile)
#   → app/models/user.py (User model)
#   → app/schemas/user.py (UserUpdateRequest)
#   → app/services/storage_service.py (optional: delete old profile photo)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
