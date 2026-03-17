<<<<<<< HEAD
from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar("T")


# ─── Paginated Response ───────────────────────
class PaginatedResponse(BaseModel, Generic[T]):
    data:     list[T]
    total:    int
    page:     int
    per_page: int


# ─── Message Response ─────────────────────────
class MessageResponse(BaseModel):
    message: str


# ─── Error Response ───────────────────────────
class ErrorResponse(BaseModel):
    detail: str
    code:   str
    # e.g. "RIDE_NOT_FOUND", "SEATS_FULL", "DUPLICATE_BOOKING"


# ─── Health Response ──────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
=======
# =============================================================================
# schemas/common.py — Shared Pydantic Schemas
# =============================================================================
# See: system-design/10-api-contracts.md §1 "Conventions"
#
# Reusable schemas used across multiple modules.
#
# NOTE: No PaginationParams schema. Pagination is done via FastAPI Query() dependencies
#       in routers (page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100))
#       rather than a shared schema — simpler and more idiomatic for query params.
#
# TODO: class PaginatedResponse(BaseModel, Generic[T]):
#       - data: list[T]
#       - total: int
#       - page: int
#       - per_page: int
#       Generic so any router can return PaginatedResponse[RideResponse] etc.
#
# TODO: class MessageResponse(BaseModel):
#       - message: str
#       For simple success responses like "Booking cancelled"
#
# TODO: class ErrorResponse(BaseModel):
#       - detail: str
#       - code: str  (e.g., "RIDE_NOT_FOUND", "SEATS_FULL")
#       See: system-design/10-api-contracts.md §12 for all 34 error codes
#
# TODO: class HealthResponse(BaseModel):
#       - status: str = "ok"
#
# Connects with:
#   → app/schemas/*.py (every schema module imports PaginatedResponse, ErrorResponse)
#   → app/routers/*.py (response_model uses these)
#   → app/utils/exceptions.py (custom exceptions return ErrorResponse shape)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
