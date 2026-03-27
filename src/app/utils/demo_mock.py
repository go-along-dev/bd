# This is a temporary memory store to bypass database issues during the live demo.
# It allows posting and fetching rides/wallet entries even if PostgreSQL is offline by using RAM.

DEMO_RIDES = []
DEMO_WALLET = {"balance": 1500.0}
DEMO_TRANSACTIONS = []
