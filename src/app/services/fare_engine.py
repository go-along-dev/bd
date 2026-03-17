<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from app.models.platform_config import PlatformConfig


class FareEngine:
    """
    Fuel-cost-sharing fare calculation engine.
    Config loaded from platform_config table with 5-min cache.
    ALWAYS uses Decimal — never float for money.
    """

    def __init__(self):
        self._cache: dict        = {}
        self._cache_loaded_at    = None
        self._cache_ttl_seconds  = 300   # 5 minutes

    # ─── Load Config ──────────────────────────
    async def load_config(self, db: AsyncSession) -> None:
        """Load fare config from platform_config. Cache for 5 minutes."""
        now = datetime.now(timezone.utc)

        # Return cached if still fresh
        if (
            self._cache_loaded_at
            and (now - self._cache_loaded_at).seconds < self._cache_ttl_seconds
            and self._cache
        ):
            return

        result = await db.execute(select(PlatformConfig))
        rows = result.scalars().all()

        config = {row.key: row.value for row in rows}

        self._cache = {
            "fuel_price_per_litre": Decimal(config.get("fuel_price_per_litre", "103.00")),
            "platform_margin_pct":  Decimal(config.get("platform_commission_pct", "10")),
            "min_fare":             Decimal(config.get("min_fare", "50.00")),
            "fare_rounding":        Decimal(config.get("fare_rounding", "5")),
        }
        self._cache_loaded_at = now

    def _round_to_nearest(self, value: Decimal, nearest: Decimal) -> Decimal:
        """Round value to nearest N (e.g. nearest ₹5)."""
        if nearest == 0:
            return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return (value / nearest).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        ) * nearest

    # ─── Full Route Fare ──────────────────────
    async def calculate_full_fare(
        self,
        db: AsyncSession,
        distance_km: float,
        mileage_kmpl: float,
        seats: int,
    ) -> dict:
        """
        Fuel-cost-sharing fare for a full ride.
        Used during ride creation.

        Algorithm:
        1. fuel_cost = (distance / mileage) * fuel_price
        2. cost_with_margin = fuel_cost * (1 + margin/100)
        3. total_fare = max(cost_with_margin, min_fare)
        4. per_seat_fare = total_fare / seats
        5. Round both to nearest ₹5
        """
        await self.load_config(db)

        d   = Decimal(str(distance_km))
        m   = Decimal(str(mileage_kmpl))
        s   = Decimal(str(seats))
        fp  = self._cache["fuel_price_per_litre"]
        pct = self._cache["platform_margin_pct"]
        mf  = self._cache["min_fare"]
        nr  = self._cache["fare_rounding"]

        # 1. Fuel cost
        fuel_cost = (d / m) * fp

        # 2. Add platform margin
        cost_with_margin = fuel_cost * (1 + pct / Decimal("100"))

        # 3. Apply minimum fare floor
        total_fare = max(cost_with_margin, mf)

        # 4. Per seat fare
        per_seat_fare = total_fare / s

        # 5. Round both to nearest ₹5
        total_fare    = self._round_to_nearest(total_fare,    nr)
        per_seat_fare = self._round_to_nearest(per_seat_fare, nr)

        return {
            "total_fare":           total_fare,
            "per_seat_fare":        per_seat_fare,
            "fuel_cost":            fuel_cost.quantize(Decimal("0.01")),
            "distance_km":          d,
            "fuel_price_per_litre": fp,
            "platform_margin_pct":  pct,
        }

    # ─── Partial Route Fare ───────────────────
    def calculate_partial_fare(
        self,
        per_seat_fare_full: Decimal,
        total_distance_km: Decimal,
        passenger_distance_km: Decimal,
        seats_booked: int = 1,
    ) -> Decimal:
        """
        Proportional fare for a passenger's partial route.
        Used during booking creation.

        Formula:
          fare = per_seat_fare_full * (passenger_distance / total_distance) * seats
        """
        if total_distance_km == 0:
            return per_seat_fare_full * seats_booked

        ratio = passenger_distance_km / total_distance_km
        fare  = per_seat_fare_full * ratio * Decimal(str(seats_booked))

        return fare.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ─── Module-level singleton ───────────────────
fare_engine = FareEngine()
=======
# =============================================================================
# services/fare_engine.py — Fare Calculation Engine
# =============================================================================
# See: system-design/05-fare-engine.md for the complete fare algorithm
# See: system-design/10-api-contracts.md §7 "Fare Engine Endpoints"
#
# Fuel-cost-sharing pricing model. No surge, no dynamic pricing for MVP.
# All money uses Decimal — NEVER float.
#
# TODO: class FareEngine:
#       Config values loaded from platform_config table (cached with short TTL):
#       - fuel_price_per_litre: Decimal (e.g. 105.00)
#       - platform_margin_pct: Decimal (e.g. 15)
#       - min_fare: Decimal (e.g. 50.00)
#       - fare_rounding: Decimal (e.g. 5)
#
# TODO: async def load_config(self, db: AsyncSession):
#       """Load fuel_price, margin, min_fare from platform_config table. Cache 5 min."""
#
# TODO: async def calculate_full_fare(
#           self, db: AsyncSession,
#           distance_km: float, mileage_kmpl: float, seats: int
#       ) → dict:
#       """
#       Fuel-cost-sharing fare calculation (used when creating a ride).
#
#       Algorithm:
#       1. fuel_cost = (distance_km / mileage_kmpl) * fuel_price_per_litre
#       2. cost_with_margin = fuel_cost * (1 + platform_margin_pct / 100)
#       3. total_fare = max(cost_with_margin, min_fare)
#       4. per_seat_fare = total_fare / seats
#       5. Round both to nearest fare_rounding (e.g. ₹5)
#       6. Return {"total_fare": Decimal, "per_seat_fare": Decimal, ...}
#
#       IMPORTANT: Use Python Decimal, not float. See 05-fare-engine.md §4.
#       """
#
# TODO: def calculate_partial_fare(
#           self,
#           per_seat_fare_full: Decimal,
#           total_distance_km: Decimal,
#           passenger_distance_km: Decimal,
#       ) → Decimal:
#       """
#       Proportional fare for a passenger's partial route.
#       Used during booking creation.
#
#       Formula:
#         fare = per_seat_fare_full * (passenger_distance_km / total_distance_km) * seats_booked
#       Round to 2 decimal places.
#       """
#
# TODO: fare_engine = FareEngine()  — module-level singleton instance
#
# Connects with:
#   → app/routers/fare.py (fare estimation endpoints)
#   → app/services/ride_service.py (calculate_full_fare on ride creation)
#   → app/services/booking_service.py (calculate_partial_fare on booking creation)
#   → app/models/platform_config.py (reads fuel_price, margin, min_fare)
#   → app/models/ride.py (reads ride.total_distance_km, ride.per_seat_fare)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
