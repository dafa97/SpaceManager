"""Check users in database."""
import asyncio
from sqlalchemy import text
from app.core.database import get_db

async def check_users():
    async for db in get_db():
        result = await db.execute(text('SELECT id, email, is_active FROM public.users'))
        users = result.fetchall()
        print("\n👥 Users in database:")
        for user in users:
            print(f"  - ID: {user[0]}, Email: {user[1]}, Active: {user[2]}")
        
        if not users:
            print("  ❌ No users found!")
        break

asyncio.run(check_users())
