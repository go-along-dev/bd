from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'b95c5b356daf'
down_revision = '856309d0de69'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id",                  UUID(),            server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("booking_id",          UUID(),            nullable=False),
        sa.Column("passenger_id",        UUID(),            nullable=False),
        sa.Column("driver_id",           UUID(),            nullable=False),
        sa.Column("amount",              sa.Numeric(10, 2), nullable=False),
        sa.Column("currency",            sa.String(3),      nullable=False, server_default="INR"),
        sa.Column("status",              sa.String(20),     nullable=False, server_default="pending"),
        sa.Column("razorpay_order_id",   sa.String(100),    nullable=True),
        sa.Column("razorpay_payment_id", sa.String(100),    nullable=True),
        sa.Column("razorpay_signature",  sa.String(255),    nullable=True),
        sa.Column("payment_method",      sa.String(50),     nullable=True),
        sa.Column("paid_at",             sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at",          sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"],   ["bookings.id"]),
        sa.ForeignKeyConstraint(["passenger_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["driver_id"],    ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id"),
    )
    op.create_index("idx_payments_booking_id",   "payments", ["booking_id"])
    op.create_index("idx_payments_passenger_id", "payments", ["passenger_id"])
    op.create_index("idx_payments_status",       "payments", ["status"])


def downgrade() -> None:
    op.drop_index("idx_payments_status")
    op.drop_index("idx_payments_passenger_id")
    op.drop_index("idx_payments_booking_id")
    op.drop_table("payments")