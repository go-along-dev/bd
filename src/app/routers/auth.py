from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, get_auth_token_payload

from app.services import auth_service
from app.models.user import User

from app.schemas.auth import AuthSyncRequest, FCMTokenRequest, AuthSyncResponse, FCMTokenResponse
from app.schemas.common import MessageResponse
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/mock-sync", response_model=AuthSyncResponse)
async def mock_sync_user(
    db: AsyncSession = Depends(get_db),
):
    """
    Bypass Supabase for testing other features.
    Hardcoded fallback in case DB is on fire.
    """
    DEMO_UID = "00000000-0000-0000-0000-000000000000"
    
    try:
        user, is_new = await auth_service.sync_user(
            db=db,
            supabase_uid=DEMO_UID,
            data=AuthSyncRequest(name="Demo User", email="demo@goalong.in", phone="0000000000"),
        )
        return {
            "id":           user.id,
            "supabase_uid": user.supabase_uid,
            "name":         user.name,
            "role":         user.role,
            "is_new_user":  is_new,
        }
    except Exception as e:
        print(f"⚠️ Mock sync DB failed: {e}. Falling back to static profile.")
        # Failsafe: Return a static profile to unblock the UI
        return {
            "id":           "d3b07384-dead-beef-cafe-d3b07384dead", 
            "supabase_uid": DEMO_UID,
            "name":         "Demo User (Failsafe)",
            "role":         "passenger",
            "is_new_user":  False,
        }


@router.post("/sync", response_model=AuthSyncResponse)
async def sync_user(
    payload: AuthSyncRequest,
    db: AsyncSession = Depends(get_db),
    auth_payload: dict = Depends(get_auth_token_payload),
):
    """
    Called once after first Supabase login.
    Creates user row + wallet on first login.
    Updates profile fields on subsequent logins.
    """
    user, is_new = await auth_service.sync_user(
        db=db,
        supabase_uid=auth_payload.get("sub"),
        data=payload,
    )
    return {
        "id":           user.id,
        "supabase_uid": user.supabase_uid,
        "name":         user.name,
        "role":         user.role,
        "is_new_user":  is_new,
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
