<<<<<<< HEAD
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal


# ─── Wallet Response ──────────────────────────
class WalletResponse(BaseModel):
    id:         UUID
    balance:    Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Transaction Response ─────────────────────
class WalletTransactionResponse(BaseModel):
    id:             UUID
    type:           str
    amount:         Decimal
    status:         str
    ride_id:        UUID | None
    toll_proof_url: str | None
    upi_id:         str | None
    admin_note:     str | None
    processed_at:   datetime | None
    created_at:     datetime

    model_config = {"from_attributes": True}


# ─── Cashback Request ─────────────────────────
class CashbackRequest(BaseModel):
    ride_id: UUID
    amount:  Decimal = Field(..., gt=0, le=500)
    # toll_proof comes as UploadFile in router — not in this schema
    # Eligibility: driver must be within 90 days of onboarding
    # Ride must be completed and belong to driver


# ─── Withdrawal Request ───────────────────────
class WithdrawalRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    upi_id: str     = Field(
        ...,
        pattern=r"^[\w.\-]+@[\w]+$"
    )
    # UPI format: username@bankname
    # e.g. rahul@okaxis, 9876543210@ybl
=======
# =============================================================================
# schemas/wallet.py — Wallet & Transaction Schemas
# =============================================================================
# See: system-design/10-api-contracts.md §9 "Wallet Endpoints"
# See: system-design/07-wallet.md for wallet flows
#
# TODO: class WalletResponse(BaseModel):
#       - id: UUID
#       - balance: Decimal
#       - created_at: datetime
#       model_config: from_attributes = True
#
# TODO: class WalletTransactionResponse(BaseModel):
#       - id: UUID
#       - txn_type: str       ("cashback" | "withdrawal")
#       - amount: Decimal
#       - status: str          ("pending" | "approved" | "rejected" | "completed")
#       - reference_id: UUID | None
#       - toll_proof_url: str | None
#       - upi_id: str | None
#       - admin_note: str | None
#       - processed_at: datetime | None
#       - created_at: datetime
#       model_config: from_attributes = True
#
# TODO: class CashbackRequest(BaseModel):
#       - booking_id: UUID     (the completed booking for which cashback is claimed)
#       - amount: Decimal = Field(..., gt=0)
#       Note: toll_proof file comes as UploadFile in the router, not in this schema
#       Eligibility: booking must be 90+ days old (configurable via platform_config)
#
# TODO: class WithdrawalRequest(BaseModel):
#       - amount: Decimal = Field(..., gt=0)  (max from platform_config.max_withdrawal_amount)
#       - upi_id: str = Field(..., pattern=r"^[\w.\-]+@[\w]+$")
#
# Connects with:
#   → app/routers/wallet.py (GET /wallet, GET /wallet/transactions, POST /wallet/cashback,
#                             POST /wallet/withdraw)
#   → app/services/wallet_service.py
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
