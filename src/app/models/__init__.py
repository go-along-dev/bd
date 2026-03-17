<<<<<<< HEAD
from app.db.postgres import Base  # noqa: F401 — ensures Base is shared

from app.models.user import User
from app.models.driver import Driver
from app.models.driver_document import DriverDocument
from app.models.ride import Ride
from app.models.booking import Booking
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.platform_config import PlatformConfig

__all__ = [
    "Base",
    "User",
    "Driver",
    "DriverDocument",
    "Ride",
    "Booking",
    "Wallet",
    "WalletTransaction",
    "PlatformConfig",
]
=======
# Models package — SQLAlchemy ORM models.
# One file per table. All inherit from app.db.base.Base.
# See: system-design/11-db-schema-ddl.md for the full DDL.
#
# Import all models here so Alembic can discover them via Base.metadata.
#
# TODO: Import all model classes here:
#   from app.models.user import User
#   from app.models.driver import Driver
#   from app.models.driver_document import DriverDocument
#   from app.models.ride import Ride
#   from app.models.booking import Booking
#   from app.models.wallet import Wallet
#   from app.models.wallet_transaction import WalletTransaction
#   from app.models.platform_config import PlatformConfig
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
