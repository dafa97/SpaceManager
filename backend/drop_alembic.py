import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def drop_alembic():
    async with AsyncSessionLocal() as session:
        await session.execute(text("DROP TABLE IF EXISTS alembic_version"))
        await session.commit()
        print("Dropped alembic_version table")

if __name__ == "__main__":
    asyncio.run(drop_alembic())
