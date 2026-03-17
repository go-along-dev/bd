<<<<<<< HEAD
from sqlalchemy import (
    Column, String, Text,
    DateTime, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.postgres import Base


class PlatformConfig(Base):
    __tablename__ = "platform_config"

    # ─── Primary Key ──────────────────────────
    id          = Column(
                    UUID(as_uuid=True),
                    primary_key=True,
                    server_default=func.gen_random_uuid()
                )

    # ─── Config Entry ─────────────────────────
    key         = Column(String(50),  nullable=False, unique=True)
    value       = Column(String(255), nullable=False)
    description = Column(Text,        nullable=True)

    # ─── Timestamps ───────────────────────────
    updated_at  = Column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(),
                    onupdate=func.now())

    # ─── Expected Seed Keys ───────────────────
    # per_km_rate                → "2.50"
    # platform_commission_pct    → "10"
    # min_fare                   → "50.00"
    # max_seats_per_booking      → "4"
    # cancellation_window_hours  → "2"
    # cashback_eligibility_days  → "90"
    # max_withdrawal_amount      → "5000.00"
=======
# =============================================================================
# models/platform_config.py — Platform Configuration ORM Model
# =============================================================================
# See: system-design/11-db-schema-ddl.md §8 "Table: platform_config"
# See: system-design/05-fare-engine.md §2 for pricing rules
#
# Key-value configuration table for platform-wide settings.
# This allows changing fare rates, limits, policies without code deploys.
# Seeded with initial values via Alembic migration (see 11-db-schema-ddl.md §13).
#
# TODO: Define PlatformConfig model mapped to "platform_config" table
# TODO: Columns:
#       - id: UUID PK
#       - key: String(50), NOT NULL, UNIQUE
#       - value: String(255), NOT NULL
#       - description: Text, nullable — human explanation of what this config does
#       - updated_at: TIMESTAMPTZ
#
# TODO: Expected seed keys:
#       - per_km_rate: "2.50" (base fare per kilometer)
#       - platform_commission_pct: "10" (percentage platform takes)
#       - min_fare: "50.00" (minimum fare floor)
#       - max_seats_per_booking: "4"
#       - cancellation_window_hours: "2" (hours before departure)
#       - cashback_eligibility_days: "90" (3 months)
#       - max_withdrawal_amount: "5000.00"
#
# Connects with:
#   → app/services/fare_engine.py (reads per_km_rate, platform_commission_pct, min_fare)
#   → app/services/booking_service.py (reads cancellation_window_hours)
#   → app/services/wallet_service.py (reads cashback_eligibility_days, max_withdrawal_amount)
#   → app/admin/views.py (admin can edit config values from dashboard)
#   → alembic/versions/ (initial migration seeds these values)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
