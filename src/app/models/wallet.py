<<<<<<< HEAD
import uuid
from sqlalchemy import (
    Column, DateTime, ForeignKey,
    Index, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.postgres import Base


class Wallet(Base):
    __tablename__ = "wallets"

    # ─── Primary Key ──────────────────────────
    id              = Column(
                        UUID(as_uuid=True),
                        primary_key=True,
                        server_default=func.gen_random_uuid()
                    )

    # ─── Owner ────────────────────────────────
    # One wallet per user
    driver_id       = Column(
                        UUID(as_uuid=True),
                        ForeignKey("drivers.id"),
                        nullable=False,
                        unique=True
                    )
    # ─── Balance ──────────────────────────────
    balance         = Column(
                        Numeric(10, 2),
                        nullable=False,
                        default=0.00
                    )

    # ─── Timestamps ───────────────────────────
    created_at      = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    updated_at      = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now(),
                        onupdate=func.now())

    # ─── Constraints ──────────────────────────
    __table_args__ = (
        CheckConstraint(
            "balance >= 0",
            name="ck_wallets_balance"
        ),
    )

    # ─── Relationships ────────────────────────
    driver          = relationship("Driver", back_populates="wallet")
    transactions    = relationship(
                        "WalletTransaction",
                        back_populates="wallet",
                        order_by="WalletTransaction.created_at.desc()"
                    )
=======
# =============================================================================
# models/wallet.py — Wallet ORM Model
# =============================================================================
# See: system-design/11-db-schema-ddl.md §9 "Table: wallets"
# See: system-design/07-wallet.md for the full wallet/cashback design
#
# Every user has exactly one wallet. Wallet holds toll cashback balance.
# Drivers earn cashback from toll receipts after 3-month eligibility period.
# Withdrawal is manual via UPI, approved by admin.
#
# TODO: Define Wallet model mapped to "wallets" table
# TODO: Columns:
#       - id: UUID PK
#       - user_id: UUID FK → users.id, NOT NULL, UNIQUE (one wallet per user)
#       - balance: Numeric(10,2), NOT NULL, default 0.00
#         CHECK: balance >= 0 (prevent negative balances)
#       - created_at, updated_at: TIMESTAMPTZ
#
# TODO: Relationships:
#       - user: relationship("User", back_populates="wallet")
#       - transactions: relationship("WalletTransaction", back_populates="wallet",
#                                     order_by="WalletTransaction.created_at.desc()")
#
# Connects with:
#   → app/models/user.py (FK: user_id → users.id)
#   → app/models/wallet_transaction.py (one-to-many: wallet has many txns)
#   → app/services/wallet_service.py (balance queries, cashback, withdrawal)
#   → app/admin/views.py (admin approves cashback/withdrawal)
#
# work by adolf.
>>>>>>> 0e6b5450dd33373090fa841d0d339a07852dc2d5
