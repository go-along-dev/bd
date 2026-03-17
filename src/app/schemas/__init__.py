<<<<<<< HEAD
from app.schemas.common import PaginatedResponse, MessageResponse, ErrorResponse, HealthResponse
from app.schemas.auth import AuthSyncRequest, AuthSyncResponse, FCMTokenRequest, FCMTokenResponse
from app.schemas.user import UserResponse, UserUpdateRequest
from app.schemas.driver import DriverRegisterRequest, DriverResponse, DriverDocumentResponse, DriverStatusResponse
from app.schemas.ride import RideCreateRequest, RideUpdateRequest, RideResponse, RideDetailResponse, RideSearchParams, GeocodingResponse
from app.schemas.booking import BookingCreateRequest, BookingResponse, BookingCancelRequest
from app.schemas.wallet import WalletResponse, WalletTransactionResponse, CashbackRequest, WithdrawalRequest
from app.schemas.fare import FareCalcResponse, PartialFareResponse
from app.schemas.chat import ChatMessageIn, ChatMessageOut, ChatHistoryResponse, UnreadCountResponse

__all__ = [
    # Common
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    "HealthResponse",
    # Auth
    "AuthSyncRequest",
    "AuthSyncResponse",
    "FCMTokenRequest",
    "FCMTokenResponse",
    # User
    "UserResponse",
    "UserUpdateRequest",
    # Driver
    "DriverRegisterRequest",
    "DriverResponse",
    "DriverDocumentResponse",
    "DriverStatusResponse",
    # Ride
    "RideCreateRequest",
    "RideUpdateRequest",
    "RideResponse",
    "RideDetailResponse",
    "RideSearchParams",
    "GeocodingResponse",
    # Booking
    "BookingCreateRequest",
    "BookingResponse",
    "BookingCancelRequest",
    # Wallet
    "WalletResponse",
    "WalletTransactionResponse",
    "CashbackRequest",
    "WithdrawalRequest",
    # Fare
    "FareCalcResponse",
    "PartialFareResponse",
    # Chat
    "ChatMessageIn",
    "ChatMessageOut",
    "ChatHistoryResponse",
    "UnreadCountResponse",
]
=======
# Schemas package — Pydantic V2 request/response models.
# See: system-design/10-api-contracts.md for every field, type, and validation rule.
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
