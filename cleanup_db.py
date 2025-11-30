import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def cleanup():
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM public.tokens"))
        await session.execute(text("DELETE FROM public.organization_members"))
        await session.execute(text("DELETE FROM public.organizations"))
        await session.execute(text("DELETE FROM public.users"))
        await session.commit()
        print("Database cleaned")

if __name__ == "__main__":
    asyncio.run(cleanup())
