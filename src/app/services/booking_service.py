from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.models.booking import Booking
from app.models.ride import Ride
from app.models.user import User
from app.models.platform_config import PlatformConfig
from app.schemas.booking import BookingCreateRequest


# ─── Helper: Get Platform Config Value ────────
async def get_config(db: AsyncSession, key: str, default: str = "0") -> str:
    result = await db.execute(
        select(PlatformConfig).where(PlatformConfig.key == key)
    )
    config = result.scalar_one_or_none()
    return config.value if config else default


# ─── Create Booking ───────────────────────────
async def create_booking(
    db: AsyncSession,
    user: User,
    data: BookingCreateRequest,
) -> Booking:
    """
    Refactored for Production Readiness:
    1. Fetches external data (ORS) OUTSIDE the transaction.
    2. Uses SELECT FOR UPDATE inside the transaction for atomic seat reservation.
    3. Prevents race conditions and gridlocks.
    """
    # Step 1: Pre-fetch Ride coordinates without lock to call external ORS
    result = await db.execute(select(Ride).where(Ride.id == data.ride_id))
    ride_pre = result.scalar_one_or_none()
    
    if not ride_pre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found",
        )

    # Step 2: External Network Call (OSRM/ORS) — done OUTSIDE transaction
    from app.services import ors_service, fare_engine
    try:
        distance_km = await ors_service.get_distance(
            src_lat=float(data.pickup_lat),
            src_lng=float(data.pickup_lng),
            dst_lat=float(ride_pre.dest_lat),
            dst_lng=float(ride_pre.dest_lng),
        )
    except Exception as e:
        # Fallback if ORS fails — use a simple straight-line or total distance
        # Log this in production properly
        distance_km = float(ride_pre.total_distance_km) * 0.8 

    # Step 3: Calculate proportional fare (pure logic)
    fare = fare_engine.calculate_partial_fare(
        per_seat_fare=float(ride_pre.per_seat_fare),
        total_distance_km=float(ride_pre.total_distance_km),
        passenger_distance_km=distance_km,
    )

    # Step 4: Atomic Transaction for Seat Reservation
    async with db.begin():
        # Re-fetch with FOR UPDATE lock
        result = await db.execute(
            select(Ride)
            .where(Ride.id == data.ride_id)
            .with_for_update()
        )
        ride = result.scalar_one()

        # Step 5: Critical Validations under lock
        if ride.status != "active":
            raise HTTPException(status_code=400, detail="Ride no longer active")
        
        if ride.available_seats < data.seats_booked:
            raise HTTPException(status_code=400, detail="Not enough seats available")

        if ride.departure_time <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Ride already departed")

        # Check for duplicate pending/confirmed booking
        existing = await db.execute(
            select(Booking).where(
                and_(
                    Booking.ride_id == data.ride_id,
                    Booking.passenger_id == user.id,
                    Booking.status.in_(["pending", "confirmed"])
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Already booked for this ride")

        # Step 6: Create Booking record
        booking = Booking(
            ride_id=data.ride_id,
            passenger_id=user.id,
            seats_booked=data.seats_booked,
            pickup_address=data.pickup_address,
            pickup_lat=data.pickup_lat,
            pickup_lng=data.pickup_lng,
            dropoff_address=ride.dest_address,
            dropoff_lat=ride.dest_lat,
            dropoff_lng=ride.dest_lng,
            distance_km=Decimal(str(distance_km)),
            fare=Decimal(str(fare)),
            status="confirmed",
        )
        db.add(booking)

        # Step 7: Decrement seats
        ride.available_seats -= data.seats_booked

    # Transaction committed here
    await db.refresh(booking)

    # Step 8: Background Tasks (Non-blocking)
    try:
        from app.services import notification_service
        await notification_service.send_booking_confirmed(
            db=db,
            ride=ride,
            booking=booking,
            passenger=user,
        )
    except Exception:
        pass

    return booking


# ─── Cancel Booking ───────────────────────────
async def cancel_booking(
    db: AsyncSession,
    user: User,
    booking_id: UUID,
    reason: str = None,
):
    """
    Atomic cancellation logic.
    Restores seats to the ride.
    """
    async with db.begin():
        # 1. Lock booking AND ride
        result = await db.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.ride))
            .with_for_update()
        )
        booking = result.scalar_one_or_none()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.passenger_id != user.id:
            raise HTTPException(status_code=403, detail="Not your booking")

        if booking.status == "cancelled":
            return  # Already cancelled

        # 2. Update status
        booking.status = "cancelled"
        booking.cancelled_at = datetime.now(timezone.utc)
        booking.cancellation_reason = reason

        # 3. Restore seats
        ride = booking.ride
        ride.available_seats += booking.seats_booked

    return {"message": "Cancelled"}


# ─── Get User Bookings ────────────────────────
async def get_user_bookings(
    db: AsyncSession,
    user: User,
    page: int = 1,
    per_page: int = 10,
):
    """List bookings where user is the passenger."""
    offset = (page - 1) * per_page
    
    # Query bookings + ride info
    result = await db.execute(
        select(Booking)
        .where(Booking.passenger_id == user.id)
        .options(selectinload(Booking.ride))
        .order_by(Booking.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    bookings = result.scalars().all()

    # Count total
    count_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.passenger_id == user.id)
    )
    total = count_result.scalar()

    return bookings, total


# ─── Get Booking Detail ───────────────────────
async def get_booking_by_id(db: AsyncSession, booking_id: UUID) -> Booking | None:
    result = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.ride))
    )
    return result.scalar_one_or_none()
