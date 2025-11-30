import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def drop_all_tables():
    async with AsyncSessionLocal() as session:
        # Get all tables in public schema
        result = await session.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename != 'alembic_version'
        """))
        tables = result.fetchall()

        # Drop all tables
        for table in tables:
            table_name = table[0]
            try:
                await session.execute(text(f"DROP TABLE IF EXISTS public.{table_name} CASCADE"))
                print(f"Dropped table: {table_name}")
            except Exception as e:
                print(f"Error dropping {table_name}: {e}")

        await session.commit()
        print("All tables dropped successfully")

if __name__ == "__main__":
    asyncio.run(drop_all_tables())
