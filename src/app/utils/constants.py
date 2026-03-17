<<<<<<< HEAD
# ─── API ──────────────────────────────────────
API_V1_PREFIX = "/api/v1"


# ─── User Roles ───────────────────────────────
ROLE_PASSENGER  = "passenger"
ROLE_DRIVER     = "driver"
ROLE_ADMIN      = "admin"
VALID_ROLES     = [ROLE_PASSENGER, ROLE_DRIVER, ROLE_ADMIN]


# ─── Driver Statuses ──────────────────────────
DRIVER_PENDING   = "pending"
DRIVER_APPROVED  = "approved"
DRIVER_REJECTED  = "rejected"
DRIVER_SUSPENDED = "suspended"


# ─── Ride Statuses ────────────────────────────
RIDE_ACTIVE    = "active"
RIDE_DEPARTED  = "departed"
RIDE_COMPLETED = "completed"
RIDE_CANCELLED = "cancelled"


# ─── Booking Statuses ─────────────────────────
BOOKING_CONFIRMED = "confirmed"
BOOKING_CANCELLED = "cancelled"
BOOKING_COMPLETED = "completed"


# ─── Wallet Transaction Types ─────────────────
TXN_CASHBACK_REQUEST    = "cashback_request"
TXN_CASHBACK_CREDITED   = "cashback_credited"
TXN_CASHBACK_REJECTED   = "cashback_rejected"
TXN_WITHDRAWAL_REQUEST  = "withdrawal_request"
TXN_WITHDRAWAL_APPROVED = "withdrawal_approved"
TXN_WITHDRAWAL_REJECTED = "withdrawal_rejected"


# ─── Wallet Transaction Statuses ──────────────
TXN_PENDING   = "pending"
TXN_APPROVED  = "approved"
TXN_REJECTED  = "rejected"
TXN_COMPLETED = "completed"


# ─── Document Types ───────────────────────────
DOC_LICENSE   = "driving_license"
DOC_RC_BOOK   = "vehicle_rc"
DOC_INSURANCE = "insurance"
DOC_AADHAR    = "aadhar"
DOC_PAN       = "pan"


# ─── Storage Buckets ──────────────────────────
BUCKET_PROFILE_PHOTOS = "profile-photos"
BUCKET_DRIVER_DOCS    = "driver-documents"
BUCKET_TOLL_PROOFS    = "toll-proofs"


# ─── Search Defaults ──────────────────────────
DEFAULT_SEARCH_RADIUS_KM = 15.0
BOUNDING_BOX_DELTA       = 0.5     # ±0.5 degrees ≈ 55km
DEFAULT_PAGE             = 1
DEFAULT_PER_PAGE         = 20
MAX_PER_PAGE             = 100


# ─── Fare Engine ──────────────────────────────
DEFAULT_FUEL_PRICE       = 103.0
DEFAULT_MILEAGE_KMPL     = 15.0
DEFAULT_PLATFORM_MARGIN  = 10.0
DEFAULT_MIN_FARE         = 50.0
DEFAULT_FARE_ROUNDING    = 5.0


# ─── Wallet ───────────────────────────────────
DEFAULT_CASHBACK_ELIGIBILITY_DAYS = 90
DEFAULT_MAX_WITHDRAWAL_AMOUNT     = 5000.0
DEFAULT_MAX_CASHBACK_PER_RIDE     = 500.0


# ─── Pagination ───────────────────────────────
CHAT_HISTORY_LIMIT = 50
=======
# =============================================================================
# utils/constants.py — Application Constants
# =============================================================================
# See: system-design/10-api-contracts.md §12 "Error Code Registry"
#
# Centralized constants. No magic strings scattered across the codebase.
#
# TODO: API version prefix
#       API_V1_PREFIX = "/api/v1"
#
# TODO: User roles
#       ROLE_PASSENGER = "passenger"
#       ROLE_DRIVER = "driver"
#       ROLE_ADMIN = "admin"
#       VALID_ROLES = [ROLE_PASSENGER, ROLE_DRIVER, ROLE_ADMIN]
#
# TODO: Driver statuses
#       DRIVER_PENDING = "pending"
#       DRIVER_APPROVED = "approved"
#       DRIVER_REJECTED = "rejected"
#       DRIVER_SUSPENDED = "suspended"
#
# TODO: Ride statuses
#       RIDE_ACTIVE = "active"
#       RIDE_DEPARTED = "departed"
#       RIDE_COMPLETED = "completed"
#       RIDE_CANCELLED = "cancelled"
#
# TODO: Booking statuses
#       BOOKING_CONFIRMED = "confirmed"
#       BOOKING_CANCELLED = "cancelled"
#       BOOKING_COMPLETED = "completed"
#
# TODO: Wallet transaction types
#       TXN_CASHBACK = "cashback"
#       TXN_WITHDRAWAL = "withdrawal"
#
# TODO: Wallet transaction statuses
#       TXN_PENDING = "pending"
#       TXN_APPROVED = "approved"
#       TXN_REJECTED = "rejected"
#       TXN_COMPLETED = "completed"
#
# TODO: Document types
#       DOC_LICENSE = "license"
#       DOC_RC_BOOK = "rc_book"
#       DOC_INSURANCE = "insurance"
#       DOC_PERMIT = "permit"
#
# TODO: Storage buckets
#       BUCKET_PROFILE_PHOTOS = "profile-photos"
#       BUCKET_DRIVER_DOCS = "driver-documents"
#       BUCKET_TOLL_PROOFS = "toll-proofs"
#
# TODO: Search defaults
#       BOUNDING_BOX_DELTA = 0.5  # ±0.5 degrees (~55km) for ride search
#       DEFAULT_PAGE = 1
#       DEFAULT_PER_PAGE = 20
#       MAX_PER_PAGE = 100
#
# Connects with:
#   → Used everywhere — models, services, routers, schemas all import from here.
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
