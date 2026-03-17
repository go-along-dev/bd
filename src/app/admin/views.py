<<<<<<< HEAD
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.user import User
from app.models.driver import Driver
from app.models.driver_document import DriverDocument
from app.models.ride import Ride
from app.models.booking import Booking
from app.models.wallet import Wallet
from app.models.wallet_transaction import WalletTransaction
from app.models.platform_config import PlatformConfig
from app.config import settings


# ─── Auth Backend ─────────────────────────────
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form     = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session.update({"admin_logged_in": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("admin_logged_in", False)


# ─── User Admin ───────────────────────────────
class UserAdmin(ModelView, model=User):
    name                   = "User"
    name_plural            = "Users"
    icon                   = "fa-solid fa-users"
    column_list            = [User.id, User.name, User.email, User.phone, User.role, User.is_active, User.created_at]
    column_searchable_list = [User.name, User.email, User.phone]
    column_filters         = [User.role, User.is_active]
    can_create             = False
    can_delete             = False


# ─── Driver Admin ─────────────────────────────
class DriverAdmin(ModelView, model=Driver):
    name           = "Driver"
    name_plural    = "Drivers"
    icon           = "fa-solid fa-car"
    column_list    = [
        Driver.id, Driver.vehicle_number, Driver.vehicle_make,
        Driver.vehicle_model, Driver.vehicle_type, Driver.seat_capacity,
        Driver.mileage_kmpl, Driver.verification_status, Driver.created_at,
    ]
    column_filters = [Driver.verification_status, Driver.vehicle_type]
    can_delete     = False
    # To approve/reject: edit the record directly and change verification_status


# ─── Driver Document Admin ────────────────────
class DriverDocumentAdmin(ModelView, model=DriverDocument):
    name        = "Driver Document"
    name_plural = "Driver Documents"
    icon        = "fa-solid fa-file"
    column_list = [
        DriverDocument.id, DriverDocument.driver_id,
        DriverDocument.doc_type, DriverDocument.status,
        DriverDocument.file_url, DriverDocument.created_at,
    ]
    can_create  = False
    can_delete  = False


# ─── Ride Admin ───────────────────────────────
class RideAdmin(ModelView, model=Ride):
    name           = "Ride"
    name_plural    = "Rides"
    icon           = "fa-solid fa-route"
    column_list    = [
        Ride.id, Ride.source_address, Ride.dest_address,
        Ride.source_city, Ride.dest_city, Ride.per_seat_fare,
        Ride.available_seats, Ride.status, Ride.departure_time,
    ]
    column_filters = [Ride.status, Ride.source_city, Ride.dest_city]
    can_create     = False
    can_delete     = False


# ─── Booking Admin ────────────────────────────
class BookingAdmin(ModelView, model=Booking):
    name           = "Booking"
    name_plural    = "Bookings"
    icon           = "fa-solid fa-ticket"
    column_list    = [
        Booking.id, Booking.ride_id, Booking.passenger_id,
        Booking.seats_booked, Booking.fare, Booking.status, Booking.booked_at,
    ]
    column_filters = [Booking.status]
    can_create     = False
    can_delete     = False


# ─── Wallet Admin ─────────────────────────────
class WalletAdmin(ModelView, model=Wallet):
    name        = "Wallet"
    name_plural = "Wallets"
    icon        = "fa-solid fa-wallet"
    column_list = [Wallet.id, Wallet.driver_id, Wallet.balance, Wallet.created_at]
    can_create  = False
    can_delete  = False


# ─── Wallet Transaction Admin ─────────────────
class WalletTransactionAdmin(ModelView, model=WalletTransaction):
    name           = "Transaction"
    name_plural    = "Wallet Transactions"
    icon           = "fa-solid fa-money-bill-transfer"
    column_list    = [
        WalletTransaction.id, WalletTransaction.wallet_id,
        WalletTransaction.type, WalletTransaction.amount,
        WalletTransaction.status, WalletTransaction.ride_id,
        WalletTransaction.upi_id, WalletTransaction.admin_note,
        WalletTransaction.created_at,
    ]
    column_filters = [WalletTransaction.type, WalletTransaction.status]
    can_create     = False
    can_delete     = False
    # To approve/reject: edit the record and change status + admin_note


# ─── Platform Config Admin ────────────────────
class PlatformConfigAdmin(ModelView, model=PlatformConfig):
    name        = "Platform Config"
    name_plural = "Platform Config"
    icon        = "fa-solid fa-gear"
    column_list = [
        PlatformConfig.key, PlatformConfig.value,
        PlatformConfig.description, PlatformConfig.updated_at,
    ]
    can_create  = True
    can_delete  = False


# ─── Setup Admin ──────────────────────────────
def setup_admin(app: FastAPI, engine: AsyncEngine) -> Admin:
    auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)

    admin = Admin(
        app,
        engine,
        authentication_backend=auth_backend,
        title="GoAlong Admin",
        base_url="/admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(DriverAdmin)
    admin.add_view(DriverDocumentAdmin)
    admin.add_view(RideAdmin)
    admin.add_view(BookingAdmin)
    admin.add_view(WalletAdmin)
    admin.add_view(WalletTransactionAdmin)
    admin.add_view(PlatformConfigAdmin)

    return admin
=======
# =============================================================================
# admin/views.py — SQLAdmin Dashboard Views & Custom Actions
# =============================================================================
# See: system-design/08-admin.md for the complete admin panel design
# See: system-design/08-admin.md §3 for custom admin actions
#
# SQLAdmin auto-generates CRUD views from SQLAlchemy models.
# Mounted at /admin in main.py. Session-based auth (separate from API JWT).
#
# TODO: Create admin authentication backend
#       - Simple username/password auth for admin panel
#       - Validate against config.ADMIN_USERNAME + config.ADMIN_PASSWORD
#       - Use SQLAdmin's AuthenticationBackend with session-based login
#       - SessionMiddleware (with APP_SECRET_KEY) must be registered in main.py
#
# TODO: Define ModelAdmin classes for each model:
#
#   class UserAdmin(ModelAdmin, model=User):
#       - column_list: [id, name, email, phone, role, is_active, created_at]
#       - column_searchable_list: [name, email, phone]
#       - column_filters: [role, is_active]
#       - can_create = False  (users created via app only)
#       - can_delete = False  (deactivate instead)
#
#   class DriverAdmin(ModelAdmin, model=Driver):
#       - column_list: [id, user.name, vehicle_number, vehicle_make, vehicle_model,
#                        vehicle_type, seat_capacity, verification_status, created_at]
#       - column_filters: [verification_status, vehicle_type]
#       - Custom actions:
#         TODO: "Approve Driver" → set verification_status='approved',
#               verified_at=now(), verified_by=admin_id,
#               send notification_service.send_driver_approved(db, user_id)
#         TODO: "Reject Driver" → set verification_status='rejected' +
#               rejection_reason, send notification_service.send_driver_rejected(db, user_id, reason)
#
#   class DriverDocumentAdmin(ModelAdmin, model=DriverDocument):
#       - column_list: [id, driver.user.name, doc_type, status, file_url]
#       - Make file_url clickable (opens in new tab to view document)
#
#   class RideAdmin(ModelAdmin, model=Ride):
#       - column_list: [id, driver.user.name, source_address, dest_address,
#                        source_city, dest_city, per_seat_fare, status, departure_time]
#       - column_filters: [status, source_city, dest_city]
#       - Read-only for now (admin observes, doesn't modify rides)
#
#   class BookingAdmin(ModelAdmin, model=Booking):
#       - column_list: [id, ride_id, passenger.name, seats_booked, fare,
#                        status, booked_at]
#       - Read-only
#
#   class WalletAdmin(ModelAdmin, model=Wallet):
#       - column_list: [id, driver.user.name, balance]
#
#   class WalletTransactionAdmin(ModelAdmin, model=WalletTransaction):
#       - column_list: [id, wallet.driver.user.name, txn_type, amount, status, created_at]
#       - column_filters: [txn_type, status]
#       - Custom actions:
#         TODO: "Approve Cashback" → wallet_service.approve_transaction()
#         TODO: "Reject Cashback" → wallet_service.reject_transaction()
#         TODO: "Approve Withdrawal" → wallet_service.approve_transaction()
#         TODO: "Reject Withdrawal" → wallet_service.reject_transaction()
#
#   class PlatformConfigAdmin(ModelAdmin, model=PlatformConfig):
#       - column_list: [key, value, description, updated_at]
#       - can_create = True
#       - can_delete = False
#       Allow admin to edit fare rates, limits, etc. without code deploy.
#
# TODO: Register all admin views in a function called from main.py:
#       def setup_admin(app: FastAPI, engine: AsyncEngine) → Admin:
#           admin = Admin(app, engine, authentication_backend=...)
#           admin.add_view(UserAdmin)
#           admin.add_view(DriverAdmin)
#           ... etc ...
#           return admin
#
# Connects with:
#   → app/main.py (mounts admin at /admin)
#   → app/models/*.py (all models registered as admin views)
#   → app/services/wallet_service.py (approve/reject transaction actions)
#   → app/services/notification_service.py (FCM push on approval/rejection)
#   → app/db/postgres.py (admin uses same async engine)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
