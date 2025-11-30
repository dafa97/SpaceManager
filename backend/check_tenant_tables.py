import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def check_tenant_tables():
    async with AsyncSessionLocal() as session:
        # Check tenant schemas
        result = await session.execute(text("SELECT nspname FROM pg_catalog.pg_namespace WHERE nspname LIKE 'tenant_%';"))
        schemas = result.fetchall()
        print('Tenant schemas:')
        for schema in schemas:
            print(f'  {schema[0]}')

        # Check tables in a specific tenant schema
        tenant_schema = 'tenant_frontend_test_org'
        try:
            result = await session.execute(text(f"SELECT tablename FROM pg_tables WHERE schemaname = '{tenant_schema}';"))
            tables = result.fetchall()
            print(f'\nTables in {tenant_schema}:')
            for table in tables:
                print(f'  {table[0]}')
        except Exception as e:
            print(f'Error checking {tenant_schema}: {e}')

        # Check spaces table in public
        result = await session.execute(text("SELECT * FROM pg_tables WHERE schemaname = 'public' AND tablename = 'spaces';"))
        public_spaces = result.fetchone()
        if public_spaces:
            print('\nSpaces table in public schema: EXISTS')
        else:
            print('\nSpaces table in public schema: NOT FOUND')

if __name__ == "__main__":
    asyncio.run(check_tenant_tables())
