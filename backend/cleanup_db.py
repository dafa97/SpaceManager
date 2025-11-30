import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def cleanup():
    async with AsyncSessionLocal() as session:
        print("Dropping public schema...")
        await session.execute(text("DROP SCHEMA public CASCADE"))
        print("Recreating public schema...")
        await session.execute(text("CREATE SCHEMA public"))
        await session.commit()
        print("Database schema reset successfully")

if __name__ == "__main__":
    asyncio.run(cleanup())
