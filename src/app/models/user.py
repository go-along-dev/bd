<<<<<<< HEAD
import uuid
from sqlalchemy import (
    Column, String, Boolean, Text, Index,
    DateTime, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base


class User(Base):
    __tablename__ = "users"

    # ─── Primary Key ──────────────────────────
    id              = Column(
                        UUID(as_uuid=True),
                        primary_key=True,
                        server_default=func.gen_random_uuid()
                    )

    # ─── Identity ─────────────────────────────
    supabase_uid    = Column(String,      nullable=False, unique=True)
    name            = Column(String(100), nullable=True)
    email           = Column(String(255), nullable=True,  unique=True)
    phone           = Column(String(15),  nullable=True,  unique=True)
    profile_photo   = Column(Text,        nullable=True)

    # ─── Role ─────────────────────────────────
    role            = Column(
                        String(20),
                        nullable=False,
                        default="passenger"
                    )

    # ─── Status ───────────────────────────────
    is_active       = Column(Boolean,  nullable=False, default=True)

    # ─── FCM ──────────────────────────────────
    fcm_token       = Column(Text, nullable=True)

    # ─── Timestamps ───────────────────────────
    created_at      = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at      = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now(),
                        onupdate=func.now())

    # ─── Constraints ──────────────────────────
    __table_args__ = (
        CheckConstraint(
            "role IN ('passenger', 'driver', 'admin')",
            name="ck_users_role"
        ),
        # Hot path index — JWT auth lookup
        Index("idx_users_supabase_uid", "supabase_uid"),
    )

 # ─── Relationships ────────────────────────
    # NOTE: wallet is on Driver, NOT User
    # NOTE: rides is on Driver, NOT User
    driver      = relationship("Driver",  back_populates="user", uselist=False)
    bookings    = relationship("Booking", back_populates="passenger")
=======
# =============================================================================
# models/user.py — User ORM Model
# =============================================================================
# See: system-design/11-db-schema-ddl.md §3 "Table: users"
# See: system-design/02-user-driver.md §1 for user lifecycle
#
# The users table is the core identity table. Every authenticated person
# has exactly one row here, linked to Supabase Auth via supabase_uid.
#
# TODO: Define User model mapped to "users" table
# TODO: Columns:
#       - id: UUID PK (server_default gen_random_uuid())
#       - supabase_uid: String, NOT NULL, UNIQUE — links to Supabase Auth user
#       - name: String(100), nullable
#       - email: String(255), nullable, UNIQUE
#       - phone: String(15), nullable, UNIQUE
#       - profile_photo: Text, nullable — Supabase Storage URL
#       - role: String(20), NOT NULL, default "passenger"
#         CHECK constraint: role IN ('passenger', 'driver', 'admin')
#       - is_active: Boolean, NOT NULL, default True
#       - fcm_token: Text, nullable — Firebase Cloud Messaging device token
#       - created_at: TIMESTAMPTZ, NOT NULL, server_default now()
#       - updated_at: TIMESTAMPTZ, NOT NULL, server_default now(), onupdate now()
#
# TODO: Relationships:
#       - driver: relationship("Driver", back_populates="user", uselist=False)
#       - bookings: relationship("Booking", back_populates="passenger")
#
# NOTE: Wallet relationship is on Driver, NOT User (wallet.driver_id → drivers.id)
# NOTE: Rides relationship is on Driver, NOT User (ride.driver_id → drivers.id)
#
# TODO: Indexes:
#       - idx_users_supabase_uid ON supabase_uid (for JWT auth lookup — hot path)
#
# Connects with:
#   → app/dependencies.py (get_current_user queries by supabase_uid)
#   → app/services/auth_service.py (creates user row after Supabase signup)
#   → app/models/driver.py (one-to-one: user.id → driver.user_id)
#   → app/models/booking.py (FK: booking.passenger_id → user.id)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
