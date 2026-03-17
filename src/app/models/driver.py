<<<<<<< HEAD
from sqlalchemy import (
    Column, String, Integer, Text,
    DateTime, ForeignKey, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base


class Driver(Base):
    __tablename__ = "drivers"

    # ─── Primary Key ──────────────────────────
    id                  = Column(
                            UUID(as_uuid=True),
                            primary_key=True,
                            server_default=func.gen_random_uuid()
                        )

    # ─── User ─────────────────────────────────
    # One driver profile per user
    user_id             = Column(
                            UUID(as_uuid=True),
                            ForeignKey("users.id"),
                            nullable=False,
                            unique=True
                        )

    # ─── Vehicle ──────────────────────────────
    vehicle_number      = Column(String(20),  nullable=False)
    vehicle_make        = Column(String(50),  nullable=False)
    vehicle_model       = Column(String(100), nullable=False)
    vehicle_type        = Column(String(30),  nullable=False)
    # sedan | suv | hatchback | mini_bus
    vehicle_color       = Column(String(30),  nullable=True)

    # ─── License ──────────────────────────────
    license_number      = Column(String(50),  nullable=False)

    # ─── Capacity & Mileage ───────────────────
    seat_capacity       = Column(Integer,        nullable=False)
    mileage_kmpl        = Column(Numeric(5, 2),  nullable=False)
    # Used by fare_engine for fuel cost calculation

    # ─── Verification ─────────────────────────
    verification_status = Column(
                            String(20),
                            nullable=False,
                            default="pending"
                        )
    # pending → approved → rejected
    rejection_reason    = Column(Text,   nullable=True)
    verified_at         = Column(DateTime(timezone=True), nullable=True)
    verified_by         = Column(UUID(as_uuid=True),      nullable=True)
    # Admin user who verified

    # ─── Onboarding ───────────────────────────
    # Set when admin approves — cashback 3-month window starts here
    onboarded_at        = Column(DateTime(timezone=True), nullable=True)

    # ─── Timestamps ───────────────────────────
    created_at          = Column(DateTime(timezone=True),
                            nullable=False, server_default=func.now())
    updated_at          = Column(DateTime(timezone=True),
                            nullable=False, server_default=func.now(),
                            onupdate=func.now())

    # ─── Constraints ──────────────────────────
    __table_args__ = (
        CheckConstraint(
            "seat_capacity BETWEEN 1 AND 8",
            name="ck_drivers_seat_capacity"
        ),
        CheckConstraint(
            "mileage_kmpl BETWEEN 1 AND 50",
            name="ck_drivers_mileage"
        ),
        CheckConstraint(
            "vehicle_type IN ('sedan', 'suv', 'hatchback', 'mini_bus')",
            name="ck_drivers_vehicle_type"
        ),
        CheckConstraint(
            "verification_status IN ('pending', 'approved', 'rejected')",
            name="ck_drivers_verification_status"
        ),
        Index("idx_drivers_user_id", "user_id"),
        Index("idx_drivers_status",  "verification_status"),
    )

    # ─── Relationships ────────────────────────
    user        = relationship("User",           back_populates="driver")
    documents   = relationship("DriverDocument", back_populates="driver",
                    cascade="all, delete-orphan")
    rides       = relationship("Ride",           back_populates="driver")
    wallet      = relationship("Wallet",         back_populates="driver",
                    uselist=False)
=======
# =============================================================================
# models/driver.py — Driver ORM Model
# =============================================================================
# See: system-design/11-db-schema-ddl.md §4 "Table: drivers"
# See: system-design/02-user-driver.md §3-§5 for driver registration flow
#
# A user becomes a driver by submitting vehicle + license info.
# One-to-one with users table. Admin must approve (status → approved) before
# the user can create rides.
#
# TODO: Define Driver model mapped to "drivers" table
# TODO: Columns:
#       - id: UUID PK
#       - user_id: UUID FK → users.id, NOT NULL, UNIQUE (one driver per user)
#       - vehicle_number: String(20), NOT NULL
#       - vehicle_make: String(50), NOT NULL — e.g. "Maruti", "Hyundai"
#       - vehicle_model: String(100), NOT NULL — e.g. "Swift Dzire"
#       - vehicle_type: String(30), NOT NULL — enum: sedan|suv|hatchback|mini_bus
#       - vehicle_color: String(30)
#       - license_number: String(50), NOT NULL
#       - seat_capacity: Integer, NOT NULL, CHECK (seat_capacity BETWEEN 1 AND 8)
#       - mileage_kmpl: Numeric(5,2), NOT NULL, CHECK (mileage_kmpl BETWEEN 1 AND 50)
#       - verification_status: String(20), NOT NULL, default "pending"
#         CHECK: status IN ('pending', 'approved', 'rejected')
#       - rejection_reason: Text, nullable — admin fills on rejection
#       - verified_at: TIMESTAMPTZ, nullable — when admin approved/rejected
#       - verified_by: UUID, nullable — admin user who verified
#       - onboarded_at: TIMESTAMPTZ, nullable — set when approved (cashback window starts here)
#       - created_at, updated_at: TIMESTAMPTZ
#
# TODO: Relationships:
#       - user: relationship("User", back_populates="driver")
#       - documents: relationship("DriverDocument", back_populates="driver", cascade="all, delete-orphan")
#       - rides: relationship("Ride", back_populates="driver")
#       - wallet: relationship("Wallet", back_populates="driver", uselist=False)
#
# TODO: Indexes:
#       - idx_drivers_user_id ON user_id (UNIQUE)
#       - idx_drivers_status ON verification_status (admin queries pending drivers)
#
# Connects with:
#   → app/models/user.py (FK: user_id → users.id)
#   → app/models/driver_document.py (one-to-many: driver has multiple docs)
#   → app/models/ride.py (one-to-many: driver has multiple rides)
#   → app/models/wallet.py (one-to-one: wallet per driver)
#   → app/services/driver_service.py (registration, status checks)
#   → app/admin/views.py (admin approves/rejects drivers)
#   → app/services/ride_service.py (checks driver.verification_status == "approved")
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
