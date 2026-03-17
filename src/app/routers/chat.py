<<<<<<< HEAD
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.dependencies import get_db, get_current_user
from app.db.mongo import get_mongo_db
from app.middleware.auth import decode_supabase_jwt
from app.models.user import User
from app.models.booking import Booking
from app.models.ride import Ride
from app.schemas.chat import ChatMessageOut, ChatHistoryResponse, UnreadCountResponse
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


# ─── WebSocket /chat/ws/{booking_id} ──────────
@router.websocket("/ws/{booking_id}")
async def websocket_chat(
    websocket: WebSocket,
    booking_id: UUID,
    token: str = Query(...),        # JWT passed as query param
    db: AsyncSession = Depends(get_db),
):
    """
    Real-time chat between passenger and driver.
    JWT passed as query param (WebSocket can't use headers).
    Cloud Run: 60-min timeout. Client sends ping every 25s.
    """
    # 1. Verify JWT manually
    try:
        payload = decode_supabase_jwt(token)
        supabase_uid = payload.get("sub")
    except HTTPException:
        await websocket.close(code=4001)
        return

    # 2. Get user from DB
    from sqlalchemy import select as sa_select
    result = await db.execute(
        sa_select(User).where(User.supabase_uid == supabase_uid)
    )
    user = result.scalar_one_or_none()
    if not user:
        await websocket.close(code=4001)
        return

    # 3. Verify user is booking participant
    try:
        booking = await chat_service.verify_participant(
            db=db,
            booking_id=booking_id,
            user_id=user.id,
        )
    except HTTPException:
        await websocket.close(code=4003)
        return

    # 4. Determine other participant
    ride_result = await db.execute(
        sa_select(Ride).where(Ride.id == booking.ride_id)
    )
    ride = ride_result.scalar_one()
    other_user_id = (
        ride.driver_id
        if booking.passenger_id == user.id
        else booking.passenger_id
    )

    # 5. Get MongoDB
    mongo_db = get_mongo_db()

    # 6. Mark existing messages as read (user opened chat)
    await chat_service.mark_as_read(mongo_db, booking_id, user.id)

    # 7. Handle WebSocket loop
    await chat_service.handle_websocket(
        websocket=websocket,
        booking_id=booking_id,
        user_id=user.id,
        other_user_id=other_user_id,
        mongo_db=mongo_db,
    )


# ─── GET /chat/{booking_id}/history ──────────
@router.get("/{booking_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    booking_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    before: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch chat history for a booking.
    Cursor-based pagination using created_at.
    Also marks all messages as read for current user.
    """
    # Verify participant
    await chat_service.verify_participant(
        db=db,
        booking_id=booking_id,
        user_id=current_user.id,
    )

    mongo_db = get_mongo_db()

    # Mark as read when history is fetched
    await chat_service.mark_as_read(mongo_db, booking_id, current_user.id)

    messages = await chat_service.get_history(
        mongo_db=mongo_db,
        booking_id=booking_id,
        before=before,
        limit=limit + 1,    # fetch one extra to check has_more
    )

    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    # Reverse to return oldest first
    messages.reverse()

    return {
        "messages": messages,
        "has_more": has_more,
    }


# ─── GET /chat/unread-count ───────────────────
@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
):
    """Get total unread message count across all bookings."""
    mongo_db = get_mongo_db()

    unread_data = await chat_service.get_unread_counts(
        mongo_db=mongo_db,
        user_id=current_user.id,
    )

    total = sum(item["unread_count"] for item in unread_data)

    return {"data": {"unread_count": total}}


# ─── PUT /chat/{booking_id}/read ──────────────
@router.put("/{booking_id}/read", response_model=dict)
async def mark_chat_as_read(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Explicitly mark all messages in this booking as read."""
    # Verify participant
    await chat_service.verify_participant(
        db=db,
        booking_id=booking_id,
        user_id=current_user.id,
    )

    mongo_db = get_mongo_db()
    await chat_service.mark_as_read(
        mongo_db=mongo_db,
        booking_id=booking_id,
        user_id=current_user.id,
    )

    return {"data": {"marked_read": True}}
=======
# =============================================================================
# routers/chat.py — Chat Endpoints (WebSocket + REST)
# =============================================================================
# See: system-design/10-api-contracts.md §8 "Chat Endpoints"
# See: system-design/06-chat.md for the complete chat architecture
#
# Prefix: /api/v1/chat
#
# Real-time chat between passenger and driver for a specific booking.
# WebSocket for live messaging, REST for history, unread counts, and mark-as-read.
#
# TODO: WebSocket /chat/ws/{booking_id}?token={jwt}
#       - Auth: JWT passed as query param (WebSocket can't use headers)
#       - Logic: Call chat_service.handle_websocket()
#         1. Verify JWT from query param (HS256 + JWT_SECRET)
#         2. Verify user is part of the booking (passenger or ride driver)
#         3. Add to ConnectionManager
#         4. Mark existing messages as read (user just opened chat)
#         5. On message received:
#            a. Validate with ChatMessageIn schema
#            b. Persist to MongoDB chat_messages collection
#            c. Forward to other participant if online
#            d. If offline → send FCM push via notification_service
#         6. On disconnect: remove from ConnectionManager
#       - IMPORTANT: Cloud Run has 60-min WebSocket timeout. Client sends ping every 25s.
#
# TODO: GET /chat/{booking_id}/history
#       - Requires: Bearer token (participant only)
#       - Query params: limit (default 50)
#       - Logic: Fetch chat history from MongoDB. Returns messages in ascending order.
#         Also marks all messages as read for current user.
#       - Response: {"data": list[ChatMessageOut]}
#
# TODO: GET /chat/unread-count
#       - Requires: Bearer token
#       - Logic: Get total unread message count across all bookings for current user
#       - Response: {"data": {"unread_count": int}}
#
# TODO: PUT /chat/{booking_id}/read
#       - Requires: Bearer token (participant only)
#       - Logic: Explicitly mark all messages in this booking's chat as read
#       - Response: {"data": {"marked_read": int}}
#
# Connects with:
#   → app/schemas/chat.py (ChatMessageIn, ChatMessageOut)
#   → app/services/chat_service.py (ConnectionManager, save_message, get_chat_history, mark_as_read)
#   → app/services/notification_service.py (FCM push for offline users)
#   → app/dependencies.py (get_current_user for REST, manual JWT verify for WebSocket)
#   → app/db/mongo.py (chat_messages collection)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
