<<<<<<< HEAD
from sqlalchemy import (
    Column, String, Text, DateTime,
    ForeignKey, Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    # ─── Primary Key ──────────────────────────
    id              = Column(
                        UUID(as_uuid=True),
                        primary_key=True,
                        server_default=func.gen_random_uuid()
                    )

    # ─── Wallet ───────────────────────────────
    wallet_id       = Column(
                        UUID(as_uuid=True),
                        ForeignKey("wallets.id", ondelete="CASCADE"),
                        nullable=False
                    )

    # ─── Type ─────────────────────────────────
    type            = Column(String(30), nullable=False)
    # cashback_request | cashback_credited | cashback_rejected
    # withdrawal_request | withdrawal_approved | withdrawal_rejected

    # ─── Amount ───────────────────────────────
    amount          = Column(Numeric(10, 2), nullable=False)

    # ─── Status ───────────────────────────────
    status          = Column(
                        String(20),
                        nullable=False,
                        default="pending"
                    )

    # ─── Cashback specific ────────────────────
    ride_id         = Column(
                        UUID(as_uuid=True),
                        ForeignKey("rides.id"),
                        nullable=True
                    )
    toll_proof_url  = Column(Text,        nullable=True)

    # ─── Withdrawal specific ──────────────────
    upi_id          = Column(String(100), nullable=True)

    # ─── Admin ────────────────────────────────
    admin_note      = Column(Text,        nullable=True)
    processed_by    = Column(
                        UUID(as_uuid=True),
                        ForeignKey("users.id"),
                        nullable=True
                    )
    processed_at    = Column(DateTime(timezone=True), nullable=True)

    # ─── Timestamps ───────────────────────────
    created_at      = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())

    # ─── Constraints ──────────────────────────
    __table_args__ = (
        CheckConstraint(
            "type IN ("
            "'cashback_request', 'cashback_credited', 'cashback_rejected',"
            "'withdrawal_request', 'withdrawal_approved', 'withdrawal_rejected'"
            ")",
            name="ck_wallet_txns_type"
        ),
        CheckConstraint(
            "amount > 0",
            name="ck_wallet_txns_amount"
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_wallet_txns_status"
        ),
        Index("idx_wallet_txns_wallet_id", "wallet_id"),
        Index("idx_wallet_txns_status",    "status"),
        Index("idx_wallet_txns_type",      "type"),
    )

    # ─── Relationships ────────────────────────
    wallet          = relationship("Wallet", back_populates="transactions")
=======
# =============================================================================
# models/wallet_transaction.py — Wallet Transaction ORM Model
# =============================================================================
# See: system-design/11-db-schema-ddl.md §10 "Table: wallet_transactions"
# See: system-design/07-wallet.md §3-§4 for cashback and withdrawal flows
#
# Immutable ledger of wallet movements. Each row is a credit (cashback)
# or debit (withdrawal). Balance is derived from SUM of transactions.
#
# TODO: Define WalletTransaction model mapped to "wallet_transactions" table
# TODO: Columns:
#       - id: UUID PK
#       - wallet_id: UUID FK → wallets.id, NOT NULL
#       - txn_type: String(20), NOT NULL
#         CHECK: txn_type IN ('cashback', 'withdrawal')
#       - amount: Numeric(10,2), NOT NULL, CHECK (amount > 0)
#       - status: String(20), NOT NULL, default "pending"
#         CHECK: status IN ('pending', 'approved', 'rejected', 'completed')
#       - reference_id: UUID, nullable — links to booking_id for cashback context
#       - toll_proof_url: Text, nullable — Supabase Storage URL for toll receipt
#       - upi_id: String(100), nullable — for withdrawals
#       - admin_note: Text, nullable — admin can leave a note on approval/rejection
#       - processed_at: TIMESTAMPTZ, nullable — when admin processed it
#       - created_at: TIMESTAMPTZ
#
# TODO: Relationships:
#       - wallet: relationship("Wallet", back_populates="transactions")
#
# TODO: Indexes:
#       - idx_wallet_txns_wallet_id ON wallet_id
#       - idx_wallet_txns_status ON status (admin queries pending txns)
#
# Connects with:
#   → app/models/wallet.py (FK: wallet_id → wallets.id)
#   → app/services/wallet_service.py (create cashback request, process withdrawal)
#   → app/services/storage_service.py (toll proof upload)
#   → app/admin/views.py (admin approve/reject actions)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
