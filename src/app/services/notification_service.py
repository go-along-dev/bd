<<<<<<< HEAD
import asyncio
from functools import partial
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.booking import Booking
from app.models.ride import Ride


# ─── Firebase Initialization ──────────────────
_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials
        from app.config import settings

        if not firebase_admin._apps:
            if settings.FCM_SERVER_KEY:
                cred = credentials.Certificate(settings.FCM_SERVER_KEY)
                firebase_admin.initialize_app(cred)
            else:
                # Dev mode — skip FCM init
                print("⚠️ FCM_SERVER_KEY not set — push notifications disabled")
                return
        _firebase_initialized = True
    except Exception as e:
        print(f"⚠️ Firebase init failed: {e}")


# ─── Core Push Sender ─────────────────────────
async def send_push(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    body: str,
    data: dict | None = None,
) -> bool:
    """
    Send FCM push notification to a user.
    Fire-and-forget — failure never blocks main flow.
    Firebase SDK is sync → runs in executor.
    """
    # 1. Get FCM token from DB
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.fcm_token:
        return False

    token = user.fcm_token

    # 2. Send in executor (firebase_admin is synchronous)
    def _send(fcm_token: str) -> bool:
        try:
            import firebase_admin.messaging as messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={k: str(v) for k, v in (data or {}).items()},
                token=fcm_token,
            )
            messaging.send(message)
            return True
        except Exception as e:
            error_str = str(e).lower()
            # Token invalid — clear it
            if "registration-token-not-registered" in error_str \
                    or "invalid-registration-token" in error_str:
                return None  # Signal to clear token
            return False

    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, partial(_send, token))

    # 3. Clear invalid token
    if result is None:
        user.fcm_token = None
        await db.commit()
        return False

    return bool(result)


# ─── Booking Notifications ────────────────────
async def send_booking_confirmed(
    db: AsyncSession,
    ride: Ride,
    booking: Booking,
    passenger: User,
) -> None:
    """Notify driver of new booking."""
    from app.models.driver import Driver
    result = await db.execute(
        select(Driver).where(Driver.id == ride.driver_id)
    )
    driver = result.scalar_one_or_none()
    if not driver:
        return

    await send_push(
        db      = db,
        user_id = driver.user_id,
        title   = "New Booking! 🎉",
        body    = f"New booking from {passenger.name or 'a passenger'}",
        data    = {"booking_id": str(booking.id), "ride_id": str(ride.id)},
    )


async def send_booking_cancelled(
    db: AsyncSession,
    booking: Booking,
) -> None:
    """Notify driver of booking cancellation."""
    from app.models.ride import Ride as RideModel
    from app.models.driver import Driver

    ride_result = await db.execute(
        select(RideModel).where(RideModel.id == booking.ride_id)
    )
    ride = ride_result.scalar_one_or_none()
    if not ride:
        return

    driver_result = await db.execute(
        select(Driver).where(Driver.id == ride.driver_id)
    )
    driver = driver_result.scalar_one_or_none()
    if not driver:
        return

    passenger_result = await db.execute(
        select(User).where(User.id == booking.passenger_id)
    )
    passenger = passenger_result.scalar_one_or_none()

    await send_push(
        db      = db,
        user_id = driver.user_id,
        title   = "Booking Cancelled",
        body    = f"Booking cancelled by {passenger.name if passenger else 'a passenger'}",
        data    = {"booking_id": str(booking.id)},
    )


# ─── Ride Notifications ───────────────────────
async def send_ride_cancelled(
    db: AsyncSession,
    booking: Booking,
) -> None:
    """Notify passenger their ride was cancelled by driver."""
    await send_push(
        db      = db,
        user_id = booking.passenger_id,
        title   = "Ride Cancelled 😔",
        body    = "Your ride has been cancelled by the driver.",
        data    = {"booking_id": str(booking.id)},
    )


async def send_ride_completed(
    db: AsyncSession,
    booking: Booking,
) -> None:
    """Notify passenger their ride is complete."""
    await send_push(
        db      = db,
        user_id = booking.passenger_id,
        title   = "Ride Completed! ✅",
        body    = "Your ride is complete. Thank you for riding with GoAlong!",
        data    = {"booking_id": str(booking.id)},
    )


# ─── Chat Notifications ───────────────────────
async def send_chat_message(
    db: AsyncSession | None = None,
    receiver_id: UUID = None,
    booking_id: UUID = None,
    content: str = "",
) -> None:
    """Notify offline user of a new chat message."""
    if not db or not receiver_id:
        return

    preview = content[:50] + "..." if len(content) > 50 else content

    await send_push(
        db      = db,
        user_id = receiver_id,
        title   = "New Message 💬",
        body    = preview,
        data    = {"booking_id": str(booking_id)},
    )


# ─── Wallet Notifications ─────────────────────
async def send_cashback_approved(
    db: AsyncSession,
    user_id: UUID,
    amount: Decimal,
) -> None:
    await send_push(
        db      = db,
        user_id = user_id,
        title   = "Cashback Approved! 🎉",
        body    = f"₹{amount} has been credited to your GoAlong wallet.",
        data    = {"type": "cashback_approved"},
    )


async def send_withdrawal_processed(
    db: AsyncSession,
    user_id: UUID,
    amount: Decimal,
) -> None:
    await send_push(
        db      = db,
        user_id = user_id,
        title   = "Withdrawal Processed ✅",
        body    = f"₹{amount} is being transferred to your UPI account.",
        data    = {"type": "withdrawal_processed"},
    )


# ─── Driver Verification Notifications ────────
async def send_driver_approved(
    db: AsyncSession,
    user_id: UUID,
) -> None:
    await send_push(
        db      = db,
        user_id = user_id,
        title   = "Application Approved! 🚗",
        body    = "Your driver application has been approved! Start publishing rides.",
        data    = {"type": "driver_approved"},
    )


async def send_driver_rejected(
    db: AsyncSession,
    user_id: UUID,
    reason: str,
) -> None:
    await send_push(
        db      = db,
        user_id = user_id,
        title   = "Application Update",
        body    = f"Your driver application was not approved: {reason}",
        data    = {"type": "driver_rejected"},
    )
=======
# =============================================================================
# services/notification_service.py — Push Notification Service (FCM)
# =============================================================================
# See: system-design/01-auth.md §5 for FCM token management
# See: system-design/06-chat.md §5 for chat offline notification flow
#
# Uses Firebase Admin SDK to send push notifications via FCM.
# Notifications are fire-and-forget — failure does not block the main flow.
#
# TODO: Initialize Firebase Admin SDK
#       - Load service account JSON from config.FCM_CREDENTIALS_JSON
#       - Initialize firebase_admin app (once, at startup or first use)
#       - Use firebase_admin.messaging module
#
# TODO: async def send_push(db: AsyncSession, user_id: UUID, title: str, body: str, data: dict | None = None) → bool:
#       """
#       Steps:
#       1. Lookup user.fcm_token from DB (needs db session)
#       2. If no token → return False (user hasn't registered for push)
#       3. Build firebase_admin.messaging.Message with notification + data payload
#       4. Send via messaging.send() (run in executor since it's sync)
#       5. Handle MessagingError — if token invalid, clear user.fcm_token
#       6. Return True on success
#
#       IMPORTANT: Run firebase calls in asyncio executor (run_in_executor)
#       since firebase_admin SDK is synchronous.
#       """
#
# TODO: async def send_booking_created(booking: Booking, passenger_name: str) → None:
#       """Push to ride driver: 'New booking from {passenger_name}' """
#
# TODO: async def send_booking_cancelled(booking: Booking, passenger_name: str) → None:
#       """Push to ride driver: 'Booking cancelled by {passenger_name}' """
#
# TODO: async def send_ride_cancelled(ride: Ride, affected_bookings: list[Booking]) → None:
#       """Push to all passengers with confirmed bookings on this ride."""
#
# TODO: async def send_chat_message(recipient_id: UUID, sender_name: str, preview: str) → None:
#       """Push for offline chat: '{sender_name}: {preview}' """
#
# TODO: async def send_cashback_approved(user_id: UUID, amount: Decimal) → None:
#       """Push: 'Your cashback of ₹{amount} has been approved!' """
#
# TODO: async def send_withdrawal_processed(user_id: UUID, amount: Decimal) → None:
#       """Push: 'Your withdrawal of ₹{amount} has been processed!' """
#
# TODO: async def send_driver_approved(db: AsyncSession, user_id: UUID) → None:
#       """Push: 'Your driver application has been approved! Start publishing rides.' """
#
# TODO: async def send_driver_rejected(db: AsyncSession, user_id: UUID, reason: str) → None:
#       """Push: 'Your driver application was rejected: {reason}' """
#
# TODO: async def send_ride_completed(db: AsyncSession, user_id: UUID, dest_address: str) → None:
#       """Push to passenger: 'Your ride to {dest_address} is complete. Thank you!' """
#
# Connects with:
#   → app/config.py (FCM_CREDENTIALS_JSON path)
#   → app/models/user.py (reads fcm_token)
#   → app/services/booking_service.py (calls send_booking_created, send_booking_cancelled)
#   → app/services/ride_service.py (calls send_ride_cancelled)
#   → app/services/chat_service.py (calls send_chat_message for offline users)
#   → app/services/wallet_service.py (calls send_cashback_approved, send_withdrawal_processed)
#   → app/admin/views.py (triggers notifications on approval actions)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
