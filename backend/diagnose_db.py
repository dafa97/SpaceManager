import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def diagnose_db():
    async with AsyncSessionLocal() as session:
        print("--- Database Diagnosis ---")
        
        # Check alembic version
        try:
            result = await session.execute(text("SELECT version_num FROM alembic_version;"))
            version = result.fetchone()
            if version:
                print(f'Alembic version: {version[0]}')
            else:
                print('Alembic version table exists but is empty')
        except Exception as e:
            print(f'Error checking alembic version: {e}')

        # Get all tables in public schema
        result = await session.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """))
        tables = result.fetchall()
        
        if not tables:
            print("\nNo tables found in public schema.")
            return

        print(f"\nFound {len(tables)} tables in public schema:")
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Get columns for each table
            try:
                cols_result = await session.execute(text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """))
                columns = cols_result.fetchall()
                for col in columns:
                    print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
            except Exception as e:
                print(f"  Error getting columns: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_db())
