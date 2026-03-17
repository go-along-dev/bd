<<<<<<< HEAD
import uuid
from sqlalchemy import (
    Column, String, Integer, Text, Boolean,
    DateTime, Index, CheckConstraint, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base


class Ride(Base):
    __tablename__ = "rides"

    # ─── Primary Key ──────────────────────────
    id                  = Column(
                            UUID(as_uuid=True),
                            primary_key=True,
                            server_default=func.gen_random_uuid()
                        )

    # ─── Driver ───────────────────────────────
    # FK → drivers.id (NOT users.id)
    driver_id           = Column(
                            UUID(as_uuid=True),
                            ForeignKey("drivers.id"),
                            nullable=False
                        )

    # ─── Source ───────────────────────────────
    source_address      = Column(Text,          nullable=False)
    source_lat          = Column(Numeric(10, 7), nullable=False)
    source_lng          = Column(Numeric(10, 7), nullable=False)
    source_city         = Column(String(100),   nullable=True)

    # ─── Destination ──────────────────────────
    dest_address        = Column(Text,          nullable=False)
    dest_lat            = Column(Numeric(10, 7), nullable=False)
    dest_lng            = Column(Numeric(10, 7), nullable=False)
    dest_city           = Column(String(100),   nullable=True)

    # ─── Schedule ─────────────────────────────
    departure_time      = Column(DateTime(timezone=True), nullable=False)

    # ─── Seats ────────────────────────────────
    total_seats         = Column(Integer, nullable=False)
    available_seats     = Column(Integer, nullable=False)

    # ─── Route (from OSRM) ────────────────────
    total_distance_km   = Column(Numeric(8, 2), nullable=False)
    estimated_duration  = Column(Integer,       nullable=True)   # minutes
    route_geometry      = Column(Text,          nullable=True)   # encoded polyline

    # ─── Fare (from fare_engine) ──────────────
    total_fare          = Column(Numeric(10, 2), nullable=False)
    per_seat_fare       = Column(Numeric(10, 2), nullable=False)

    # ─── Status ───────────────────────────────
    status              = Column(
                            String(20),
                            nullable=False,
                            default="active"
                        )

    # ─── Timestamps ───────────────────────────
    created_at          = Column(DateTime(timezone=True),
                            nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True),
                            nullable=False, server_default=func.now(),
                            onupdate=func.now())

    # ─── Constraints ──────────────────────────
    __table_args__ = (
        CheckConstraint(
            "total_seats BETWEEN 1 AND 8",
            name="ck_rides_total_seats"
        ),
        CheckConstraint(
            "available_seats >= 0 AND available_seats <= total_seats",
            name="ck_rides_available_seats"
        ),
        CheckConstraint(
            "status IN ('active', 'departed', 'completed', 'cancelled')",
            name="ck_rides_status"
        ),
        # Partial index — only active rides (hot path for search)
        Index(
            "idx_rides_search",
            "status", "departure_time",
            postgresql_where=("status = 'active'")
        ),
        Index("idx_rides_source_geo", "source_lat", "source_lng"),
        Index("idx_rides_dest_geo",   "dest_lat",   "dest_lng"),
        Index("idx_rides_driver_id",  "driver_id"),
    )

    # ─── Relationships ────────────────────────
    driver              = relationship("Driver",   back_populates="rides")
    bookings            = relationship("Booking",  back_populates="ride")
=======
# =============================================================================
# models/ride.py — Ride ORM Model
# =============================================================================
# See: system-design/11-db-schema-ddl.md §6 "Table: rides"
# See: system-design/03-rides.md for full ride lifecycle
# See: system-design/05-fare-engine.md for pricing integration
#
# A ride is created by an approved driver offering seats on a route.
# Contains origin/destination coordinates, departure time, fare, available seats.
# Search uses bounding-box query on lat/lng columns — no PostGIS needed.
#
# TODO: Define Ride model mapped to "rides" table
# TODO: Columns:
#       - id: UUID PK
#       - driver_id: UUID FK → drivers.id, NOT NULL (references drivers table, NOT users)
#       - source_address: Text, NOT NULL
#       - source_lat: Numeric(10,7), NOT NULL
#       - source_lng: Numeric(10,7), NOT NULL
#       - source_city: String(100), nullable — extracted for admin display
#       - dest_address: Text, NOT NULL
#       - dest_lat: Numeric(10,7), NOT NULL
#       - dest_lng: Numeric(10,7), NOT NULL
#       - dest_city: String(100), nullable — extracted for admin display
#       - departure_time: TIMESTAMPTZ, NOT NULL
#       - total_seats: Integer, NOT NULL, CHECK (total_seats BETWEEN 1 AND 8)
#       - available_seats: Integer, NOT NULL, CHECK (available_seats >= 0 AND available_seats <= total_seats)
#       - total_distance_km: Numeric(8,2), NOT NULL — from OSRM route API
#       - estimated_duration: Integer, nullable — minutes from OSRM
#       - route_geometry: Text, nullable — encoded polyline for map display
#       - total_fare: Numeric(10,2), NOT NULL — calculated by fare_engine
#       - per_seat_fare: Numeric(10,2), NOT NULL — total_fare / total_seats
#       - status: String(20), NOT NULL, default "active"
#         CHECK: status IN ('active', 'departed', 'completed', 'cancelled')
#       - created_at, updated_at: TIMESTAMPTZ
#
# TODO: Relationships:
#       - driver: relationship("Driver", back_populates="rides")
#       - bookings: relationship("Booking", back_populates="ride")
#
# TODO: Indexes:
#       - idx_rides_search: composite on (status, departure_time) WHERE status = 'active'
#       - idx_rides_source_geo ON (source_lat, source_lng)
#       - idx_rides_dest_geo ON (dest_lat, dest_lng)
#       - idx_rides_driver_id ON driver_id
#
# Connects with:
#   → app/models/driver.py (FK: driver_id → drivers.id)
#   → app/models/booking.py (one-to-many: ride has multiple bookings)
#   → app/services/ride_service.py (CRUD, search, depart, complete)
#   → app/services/osrm_service.py (distance calculation on creation)
#   → app/services/fare_engine.py (fare calculation on creation)
#   → app/services/booking_service.py (reads ride, decrements available_seats)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
