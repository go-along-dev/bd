<<<<<<< HEAD
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user

from app.services import auth_service
from app.models.user import User

from app.schemas.auth import AuthSyncRequest, FCMTokenRequest, AuthSyncResponse, FCMTokenResponse
from app.schemas.common import MessageResponse
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sync", response_model=AuthSyncResponse)
async def sync_user(
    payload: AuthSyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Called once after first Supabase login.
    Creates user row + wallet on first login.
    Updates profile fields on subsequent logins.
    """
    user, is_new = await auth_service.sync_user(
        db=db,
        supabase_uid=current_user.supabase_uid,
        data=payload,
    )
    return {
        "message": "Welcome to GoAlong!" if is_new else "Welcome back!",
        "is_new_user": is_new,
    }


@router.post("/fcm-token", response_model=MessageResponse)
async def register_fcm_token(
    payload: FCMTokenRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register FCM device token for push notifications."""
    await auth_service.update_fcm_token(db, current_user, payload.token)
    return {"message": "FCM token registered"}


@router.delete("/fcm-token", response_model=MessageResponse)
async def remove_fcm_token(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove FCM token on logout."""
    await auth_service.remove_fcm_token(db, current_user)
    return {"message": "FCM token removed"}
=======
# =============================================================================
# routers/auth.py — Auth Endpoints
# =============================================================================
# See: system-design/10-api-contracts.md §2 "Auth Endpoints"
# See: system-design/01-auth.md for the complete auth architecture
#
# Prefix: /api/v1/auth
#
# Supabase handles actual authentication (OTP, email signup, JWT issuance).
# These endpoints handle post-authentication sync with our database.
#
# TODO: POST /auth/sync
#       - Requires: Bearer token (Supabase JWT)
#       - Request body: AuthSyncRequest
#       - Logic: Call auth_service.sync_user() which:
#         1. Verifies JWT and extracts supabase_uid
#         2. Upserts user row in users table
#         3. Returns user data + is_new_user flag
#       - Response: AuthSyncResponse
#       - Called by Flutter app immediately after Supabase login/signup
#
# TODO: POST /auth/fcm-token
#       - Requires: Bearer token
#       - Request body: FCMTokenRequest
#       - Logic: Call auth_service.update_fcm_token()
#         Updates the user's fcm_token column for push notifications
#       - Response: FCMTokenResponse
#       - Called by Flutter on app launch and when FCM token refreshes
#
# Connects with:
#   → app/schemas/auth.py (AuthSyncRequest, AuthSyncResponse, FCMTokenRequest)
#   → app/services/auth_service.py (sync_user, update_fcm_token)
#   → app/dependencies.py (get_current_user, get_db)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
