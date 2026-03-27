import asyncio
import sys
import os

# Ensure the app code is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.postgres import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

async def check_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).limit(5))
        users = result.scalars().all()
        for u in users:
            print(f"User ID: {u.id}, UID: {u.supabase_uid}, Name: {u.name}")

if __name__ == "__main__":
    asyncio.run(check_users())
