<<<<<<< HEAD
from app.services import auth_service
from app.services import user_service
from app.services import driver_service
from app.services import storage_service
from app.services import osrm_service
from app.services import fare_engine
from app.services import ride_service
from app.services import booking_service
from app.services import wallet_service
from app.services import chat_service
from app.services import notification_service

__all__ = [
    "auth_service",
    "user_service",
    "driver_service",
    "storage_service",
    "osrm_service",
    "fare_engine",
    "ride_service",
    "booking_service",
    "wallet_service",
    "chat_service",
    "notification_service",
]
=======
# Services package — Business logic layer.
# ALL business logic lives here. Routers are thin wrappers.
# See: 00-architecture.md §8 note 4 — "One service per module."
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
