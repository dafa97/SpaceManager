import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def check_tables():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public';"))
        tables = result.fetchall()
        print('Public schema tables:')
        for table in tables:
            print(f'  {table[1]}')

        # Check alembic version
        result = await session.execute(text("SELECT version_num FROM alembic_version;"))
        version = result.fetchone()
        if version:
            print(f'Alembic version: {version[0]}')
        else:
            print('No alembic version found')

if __name__ == "__main__":
    asyncio.run(check_tables())
