<<<<<<< HEAD
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
    driver = await get_driver(db, current_user)
    return await ride_service.create_ride(db=db, driver=driver, data=payload)


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
    params = RideSearchParams(
        source_lat = source_lat,
        source_lng = source_lng,
        dest_lat   = dest_lat,
        dest_lng   = dest_lng,
        date       = date,
        seats      = seats,
        radius_km  = radius_km,
    )
    return await ride_service.search_rides(db=db, params=params)


# ─── GET /rides/my-rides ──────────────────────
@router.get("/my-rides", response_model=dict)
async def get_my_rides(
    db: AsyncSession        = Depends(get_db),
    current_user: User      = Depends(require_driver),
    pagination: dict        = Depends(get_pagination),
):
    """Get all rides created by current driver."""
    driver = await get_driver(db, current_user)
    rides, total = await ride_service.get_driver_rides(
        db       = db,
        driver   = driver,
        page     = pagination["page"],
        per_page = pagination["per_page"],
    )
    return {
        "data":     [RideResponse.model_validate(r) for r in rides],
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
    return ride


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
    return await ride_service.update_ride(db=db, ride=ride, data=payload)


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
    return await ride_service.depart_ride(db=db, ride=ride)


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
    return await ride_service.complete_ride(db=db, ride=ride)
=======
# =============================================================================
# routers/rides.py — Ride CRUD & Search Endpoints
# =============================================================================
# See: system-design/10-api-contracts.md §5 "Ride Endpoints"
# See: system-design/03-rides.md for the complete ride module design
#
# Prefix: /api/v1/rides
#
# TODO: POST /rides
#       - Requires: Bearer token (role: driver, verification_status: approved)
#       - Request body: RideCreateRequest
#       - Logic: Call ride_service.create_ride(db, driver, data)
#         1. Verify driver.verification_status == "approved"
#         2. Verify data.total_seats <= driver.seat_capacity
#         3. Call osrm_service.get_route(src, dst) for distance, duration, geometry
#         4. Call fare_engine.calculate_full_fare(db, distance, mileage, seats)
#         5. Insert ride row with driver_id → drivers.id
#       - Response: RideDetailResponse (201 Created)
#
# TODO: GET /rides
#       - Requires: Bearer token
#       - Query params: src_lat, src_lng, dst_lat, dst_lng, date, radius_km=15.0
#       - Logic: Call ride_service.search_rides()
#         Bounding box query with configurable radius (default 15km)
#         Filter: status = 'active', departure_time on requested date, available_seats > 0
#       - Response: list[RideResponse]
#
# TODO: GET /rides/{ride_id}
#       - Requires: Bearer token
#       - Logic: Return single ride with driver info. Auto-depart stale rides.
#       - Response: RideDetailResponse
#
# TODO: GET /rides/my-rides
#       - Requires: Bearer token (role: driver)
#       - Logic: Return all rides created by current driver
#       - Response: list[RideResponse]
#
# TODO: GET /rides/{ride_id}/bookings
#       - Requires: Bearer token (ride owner only)
#       - Logic: Return all bookings for a ride — driver can see their passengers
#       - Response: list[BookingResponse]
#
# TODO: PUT /rides/{ride_id}
#       - Requires: Bearer token (ride owner only)
#       - Request body: RideUpdateRequest
#       - Logic: Update ride — departure_time only if no bookings, total_seats if >= booked
#       - Response: RideDetailResponse
#
# TODO: DELETE /rides/{ride_id}
#       - Requires: Bearer token (ride owner only)
#       - Logic: Cancel ride (set status = 'cancelled')
#         Also cancel all confirmed bookings and notify passengers via FCM
#       - Response: MessageResponse
#
# TODO: POST /rides/{ride_id}/depart
#       - Requires: Bearer token (ride owner only)
#       - Logic: Mark ride as departed — no new bookings accepted
#       - Response: RideDetailResponse
#
# TODO: POST /rides/{ride_id}/complete
#       - Requires: Bearer token (ride owner only)
#       - Logic: Complete ride — settle all bookings, credit driver wallet
#         1. Set ride status = 'completed'
#         2. Set all confirmed bookings to 'completed'
#         3. Credit total earnings to driver's wallet
#         4. Notify all passengers via FCM
#       - Response: RideDetailResponse
#
# TODO: GET /rides/geocode
#       - Requires: Bearer token
#       - Query param: q (address string)
#       - Logic: Call ride_service.geocode() → Nominatim API
#       - Response: list[GeocodingResponse]
#
# Connects with:
#   → app/schemas/ride.py (RideCreateRequest, RideUpdateRequest, RideResponse, RideDetailResponse, RideSearchParams)
#   → app/services/ride_service.py (create, search, geocode, cancel, depart, complete)
#   → app/services/osrm_service.py (distance calculation)
#   → app/services/fare_engine.py (fare calculation)
#   → app/services/notification_service.py (notify passengers on ride events)
#   → app/services/wallet_service.py (credit driver on ride completion)
#   → app/dependencies.py (get_current_user, get_db)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
