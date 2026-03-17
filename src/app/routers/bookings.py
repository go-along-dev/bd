<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.dependencies import get_db, get_current_user, get_pagination
from app.schemas.booking import (
    BookingCreateRequest,
    BookingResponse,
    BookingCancelRequest,
)
from app.services import booking_service
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ─── POST /bookings ───────────────────────────
@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_booking(
    payload: BookingCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Book a seat on a ride.
    CRITICAL: Uses SELECT FOR UPDATE to prevent race conditions.
    Calculates partial fare based on pickup → destination distance.
    """
    return await booking_service.create_booking(
        db=db,
        user=current_user,
        data=payload,
    )


# ─── GET /bookings ────────────────────────────
@router.get("", response_model=dict)
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination: dict = Depends(get_pagination),
):
    """Get all bookings for the current user as passenger."""
    bookings, total = await booking_service.get_user_bookings(
        db=db,
        user=current_user,
        page=pagination["page"],
        per_page=pagination["per_page"],
    )
    return {
        "data":     [BookingResponse.model_validate(b) for b in bookings],
        "total":    total,
        "page":     pagination["page"],
        "per_page": pagination["per_page"],
    }


# ─── GET /bookings/{booking_id} ───────────────
@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific booking. Only accessible by booking owner or ride driver."""
    booking = await booking_service.get_booking_by_id(db, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Only passenger or ride's driver can view
    is_passenger = booking.passenger_id == current_user.id
    is_driver = booking.ride.driver_id == current_user.id

    if not is_passenger and not is_driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return booking


# ─── DELETE /bookings/{booking_id} ────────────
@router.delete("/{booking_id}", response_model=dict)
async def cancel_booking(
    booking_id: UUID,
    payload: BookingCancelRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel a booking.
    Only allowed if departure_time - now() > cancellation_window_hours.
    Restores seats to ride. Notifies driver via FCM.
    """
    await booking_service.cancel_booking(
        db=db,
        user=current_user,
        booking_id=booking_id,
        reason=payload.cancellation_reason if payload else None,
    )
    return {"message": "Booking cancelled successfully"}
=======
# =============================================================================
# routers/bookings.py — Booking Endpoints
# =============================================================================
# See: system-design/10-api-contracts.md §6 "Booking Endpoints"
# See: system-design/04-bookings.md for the complete booking module design
# See: HLD diagram §2.4 in 00-architecture.md for end-to-end booking flow
#
# Prefix: /api/v1/bookings
#
# TODO: POST /bookings
#       - Requires: Bearer token (role: passenger or driver booking someone else's ride)
#       - Request body: BookingCreateRequest
#       - Logic: Call booking_service.create_booking()
#         CRITICAL — this is the most complex endpoint:
#         1. SELECT ride FOR UPDATE (row lock — prevents race conditions)
#         2. Validate: ride active, not departed, seats available, not own ride, not duplicate
#         3. Call osrm_service.get_route_distance(pickup → ride destination) for partial_distance_km
#         4. Call fare_engine.calculate_partial_fare(distance, ride.per_km_rate) for fare_amount
#         5. INSERT booking, UPDATE ride.available_seats (atomic in same transaction)
#         6. COMMIT
#         7. Send FCM push to driver: "New booking from {passenger_name}"
#       - Response: BookingResponse (201 Created)
#       - Errors: RIDE_NOT_FOUND, RIDE_NOT_ACTIVE, SEATS_FULL, SELF_BOOKING, DUPLICATE_BOOKING
#
# TODO: GET /bookings
#       - Requires: Bearer token
#       - Logic: Return all bookings for current user (as passenger)
#       - Response: PaginatedResponse[BookingResponse]
#
# TODO: GET /bookings/{booking_id}
#       - Requires: Bearer token (booking owner or ride driver)
#       - Response: BookingResponse
#
# TODO: DELETE /bookings/{booking_id}
#       - Requires: Bearer token (booking owner only)
#       - Request body: BookingCancelRequest (optional reason)
#       - Logic: Call booking_service.cancel_booking()
#         1. Check cancellation window: departure_time - now() > 2 hours
#         2. Set booking.status = 'cancelled'
#         3. Increment ride.available_seats
#         4. Send FCM push to driver: "Booking cancelled"
#       - Response: MessageResponse
#       - Error: CANCELLATION_WINDOW_CLOSED if < 2 hours to departure
#
# Connects with:
#   → app/schemas/booking.py (BookingCreateRequest, BookingResponse, BookingCancelRequest)
#   → app/services/booking_service.py (create, cancel, list)
#   → app/services/fare_engine.py (partial fare calc)
#   → app/services/osrm_service.py (partial distance)
#   → app/services/notification_service.py (FCM push to driver)
#   → app/dependencies.py (get_current_user, get_db)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
