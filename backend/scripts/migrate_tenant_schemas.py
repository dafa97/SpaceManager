"""
Script to migrate existing tenant schemas to the correct structure.

This script:
1. Finds all tenant schemas
2. Checks if they have the correct tables (spaces and reservations)
3. Creates missing tables with the correct structure
4. Updates existing tables if needed
"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.tenant_schema import init_tenant_schema


async def get_all_tenant_schemas(db) -> list[str]:
    """Get all tenant schema names from the database."""
    result = await db.execute(text("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name LIKE 'tenant_%'
        ORDER BY schema_name
    """))
    return [row[0] for row in result.fetchall()]


async def schema_has_table(db, schema_name: str, table_name: str) -> bool:
    """Check if a schema has a specific table."""
    result = await db.execute(text("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_schema = :schema_name 
            AND table_name = :table_name
        )
    """), {"schema_name": schema_name, "table_name": table_name})
    return result.scalar()


async def migrate_tenant_schemas():
    """Migrate all existing tenant schemas to the correct structure."""
    async with AsyncSessionLocal() as db:
        print("=== Migrating Tenant Schemas ===\n")
        
        # Get all tenant schemas
        schemas = await get_all_tenant_schemas(db)
        
        if not schemas:
            print("No tenant schemas found.")
            return
        
        print(f"Found {len(schemas)} tenant schema(s):\n")
        
        for schema_name in schemas:
            print(f"Processing schema: {schema_name}")
            
            # Check current state
            has_spaces = await schema_has_table(db, schema_name, "spaces")
            has_reservations = await schema_has_table(db, schema_name, "reservations")
            
            print(f"  - spaces table: {'✓' if has_spaces else '✗'}")
            print(f"  - reservations table: {'✓' if has_reservations else '✗'}")
            
            # Initialize schema (will create missing tables)
            try:
                await init_tenant_schema(db, schema_name)
                print(f"  ✓ Schema {schema_name} initialized successfully")
            except Exception as e:
                print(f"  ✗ Error initializing {schema_name}: {e}")
            
            print()
        
        print("=== Migration Complete ===")


if __name__ == "__main__":
    asyncio.run(migrate_tenant_schemas())

