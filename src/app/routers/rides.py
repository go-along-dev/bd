from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import date

from app.dependencies import get_db, get_current_user, require_driver, get_pagination
from app.schemas.ride import (
    RideCreateRequest, RideUpdateRequest,
    RideResponse, RideDetailResponse,
    RideSearchParams, GeocodingResponse,
)
from app.schemas.booking import BookingResponse
from app.services import ride_service
from app.models.user import User
from app.models.driver import Driver
from app.models.ride import Ride

router = APIRouter(prefix="/rides", tags=["Rides"])


# ─── Helper: Get Driver ───────────────────────
async def get_driver(db: AsyncSession, user: User) -> Driver:
    # --- Demo Bypass ---
    if user.supabase_uid == "00000000-0000-0000-0000-000000000000":
        return Driver(
            id=user.id, # Using user.id as driver.id for mock
            user_id=user.id,
            vehicle_model="Demo Car",
            vehicle_number="GA-000-DEMO",
            is_approved=True
        )
    # -------------------

    result = await db.execute(
        select(Driver).where(Driver.user_id == user.id)
    )
    driver = result.scalar_one_or_none()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    return driver


# ─── Helper: Get Ride & Verify Ownership ─────
async def get_owned_ride(
    ride_id: UUID,
    db: AsyncSession,
    driver: Driver,
) -> Ride:
    result = await db.execute(
        select(Ride).where(Ride.id == ride_id)
    )
    ride = result.scalar_one_or_none()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.driver_id != driver.id:
        raise HTTPException(status_code=403, detail="Not your ride")
    return ride


# ─── POST /rides ──────────────────────────────
@router.post("", response_model=RideDetailResponse, status_code=201)
async def create_ride(
    payload: RideCreateRequest,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    """Create a new ride. Driver must be approved."""
    if current_user.supabase_uid == "00000000-0000-0000-0000-000000000000":
        from app.utils.demo_mock import DEMO_RIDES
        from decimal import Decimal
        import uuid
        from datetime import datetime, timezone
        
        # In-memory storage for Demo
        ride_id = uuid.uuid4()
        mock_ride = {
            "id":                 ride_id,
            "driver_name":        current_user.name,
            "vehicle_info":       "Demo Car · White · GA-000-DEMO",
            "source_address":     payload.source_address,
            "source_lat":         payload.source_lat,
            "source_lng":         payload.source_lng,
            "dest_address":       payload.dest_address,
            "dest_lat":           payload.dest_lat,
            "dest_lng":           payload.dest_lng,
            "total_distance_km":  Decimal("45.5"),
            "estimated_duration": 65,
            "departure_time":     payload.departure_time,
            "total_seats":        payload.total_seats,
            "available_seats":    payload.total_seats,
            "per_seat_fare":      Decimal("350.00"),
            "total_fare":         Decimal("350.00"),
            "status":             "booking_open",
            "created_at":         datetime.now(timezone.utc),
            "route_geometry":     None,
        }
        DEMO_RIDES.insert(0, mock_ride) # Head first
        return mock_ride

    driver = await get_driver(db, current_user)
    ride = await ride_service.create_ride(db=db, driver=driver, data=payload)
    return ride_service.build_ride_response(ride)


# ─── GET /rides (search) ──────────────────────
@router.get("", response_model=list[RideResponse])
async def search_rides(
    source_lat:  float = Query(..., ge=-90,  le=90),
    source_lng:  float = Query(..., ge=-180, le=180),
    dest_lat:    float = Query(..., ge=-90,  le=90),
    dest_lng:    float = Query(..., ge=-180, le=180),
    date:        date  = Query(...),
    seats:       int   = Query(default=1, ge=1, le=8),
    radius_km:   float = Query(default=15.0, ge=1, le=100),
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search rides by location and date using bounding box algorithm."""
    if current_user.supabase_uid == "00000000-0000-0000-0000-000000000000":
        from app.utils.demo_mock import DEMO_RIDES
        return DEMO_RIDES # Return everything for the demo

    params = RideSearchParams(
        source_lat = source_lat,
        source_lng = source_lng,
        dest_lat   = dest_lat,
        dest_lng   = dest_lng,
        date       = date,
        seats      = seats,
        radius_km  = radius_km,
    )
    rides = await ride_service.search_rides(db=db, params=params)
    return [ride_service.build_ride_response(r) for r in rides]


# ─── GET /rides/my-rides ──────────────────────
@router.get("/my-rides", response_model=dict)
async def get_my_rides(
    db: AsyncSession        = Depends(get_db),
    current_user: User      = Depends(require_driver),
    pagination: dict        = Depends(get_pagination),
):
    """Get all rides created by current driver."""
    if current_user.supabase_uid == "00000000-0000-0000-0000-000000000000":
        from app.utils.demo_mock import DEMO_RIDES
        return {
            "data":     DEMO_RIDES,
            "total":    len(DEMO_RIDES),
            "page":     1,
            "per_page": 20,
        }

    driver = await get_driver(db, current_user)
    rides, total = await ride_service.get_driver_rides(
        db       = db,
        driver   = driver,
        page     = pagination["page"],
        per_page = pagination["per_page"],
    )
    return {
        "data":     [ride_service.build_ride_response(r) for r in rides],
        "total":    total,
        "page":     pagination["page"],
        "per_page": pagination["per_page"],
    }


# ─── GET /rides/geocode ───────────────────────
@router.get("/geocode", response_model=list[GeocodingResponse])
async def geocode(
    q: str             = Query(..., min_length=3),
    current_user: User = Depends(get_current_user),
):
    """Geocode an address using Nominatim (India only)."""
    if current_user.supabase_uid == "00000000-0000-0000-0000-000000000000":
        return [
            {"display_name": f"{q}, Demo City, GA", "lat": 13.0827, "lng": 80.2707},
            {"display_name": f"{q} Downtown, Demo City", "lat": 12.9716, "lng": 77.5946},
        ]

    return await ride_service.geocode(query=q)


# ─── GET /rides/{ride_id} ─────────────────────
@router.get("/{ride_id}", response_model=RideDetailResponse)
async def get_ride(
    ride_id: UUID,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ride details. Auto-transitions stale active → departed."""
    ride = await ride_service.get_ride_by_id(db=db, ride_id=ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride_service.build_ride_response(ride)


# ─── GET /rides/{ride_id}/bookings ────────────
@router.get("/{ride_id}/bookings", response_model=list[BookingResponse])
async def get_ride_bookings(
    ride_id: UUID,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    """Get all bookings for a ride. Only ride owner can access."""
    driver = await get_driver(db, current_user)
    return await ride_service.get_ride_bookings(
        db=db, ride_id=ride_id, driver=driver
    )


# ─── PUT /rides/{ride_id} ─────────────────────
@router.put("/{ride_id}", response_model=RideDetailResponse)
async def update_ride(
    ride_id: UUID,
    payload: RideUpdateRequest,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    """Update ride. Cannot change departure_time if bookings exist."""
    driver = await get_driver(db, current_user)
    ride   = await get_owned_ride(ride_id, db, driver)
    updated_ride = await ride_service.update_ride(db=db, ride=ride, data=payload)
    return ride_service.build_ride_response(updated_ride)


# ─── DELETE /rides/{ride_id} ──────────────────
@router.delete("/{ride_id}", response_model=dict)
async def cancel_ride(
    ride_id: UUID,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    """Cancel ride. Cancels all bookings and notifies passengers."""
    driver = await get_driver(db, current_user)
    ride   = await get_owned_ride(ride_id, db, driver)
    await ride_service.cancel_ride(db=db, ride=ride)
    return {"message": "Ride cancelled successfully"}


# ─── POST /rides/{ride_id}/depart ────────────
@router.post("/{ride_id}/depart", response_model=RideDetailResponse)
async def depart_ride(
    ride_id: UUID,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    """Mark ride as departed. No new bookings accepted."""
    driver = await get_driver(db, current_user)
    ride   = await get_owned_ride(ride_id, db, driver)
    departed_ride = await ride_service.depart_ride(db=db, ride=ride)
    return ride_service.build_ride_response(departed_ride)


# ─── POST /rides/{ride_id}/complete ──────────
@router.post("/{ride_id}/complete", response_model=RideDetailResponse)
async def complete_ride(
    ride_id: UUID,
    db: AsyncSession   = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    """
    Complete ride.
    Completes all bookings and notifies passengers.
    """
    driver = await get_driver(db, current_user)
    ride   = await get_owned_ride(ride_id, db, driver)
    completed_ride = await ride_service.complete_ride(db=db, ride=ride)
    return ride_service.build_ride_response(completed_ride)
