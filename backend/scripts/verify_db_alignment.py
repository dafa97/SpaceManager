"""
Script to verify that database tables are aligned with SQLAlchemy models.
"""
import asyncio
from sqlalchemy import text, inspect
from app.core.database import AsyncSessionLocal, engine
from app.models.space import Space
from app.models.reservation import Reservation


async def verify_alignment():
    """Verify that database tables match SQLAlchemy models."""
    async with AsyncSessionLocal() as db:
        print("=== Verifying Database Alignment ===\n")
        
        # Get a sample tenant schema
        result = await db.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name LIKE 'tenant_%'
            LIMIT 1
        """))
        row = result.fetchone()
        
        if not row:
            print("No tenant schemas found.")
            return
        
        schema_name = row[0]
        print(f"Verifying schema: {schema_name}\n")
        
        # Verify spaces table
        print("Verifying spaces table:")
        result = await db.execute(text(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = :schema_name AND table_name = 'spaces'
            ORDER BY ordinal_position
        """), {"schema_name": schema_name})
        
        db_columns = {row[0]: (row[1], row[2]) for row in result.fetchall()}
        
        # Expected columns from Space model
        expected_columns = {
            'id': ('integer', 'NO'),
            'name': ('character varying', 'NO'),
            'description': ('text', 'YES'),
            'space_type': ('character varying', 'NO'),
            'capacity': ('integer', 'YES'),
            'price_per_unit': ('numeric', 'NO'),
            'is_available': ('boolean', 'NO'),
            'floor': ('character varying', 'YES'),
            'area_sqm': ('numeric', 'YES'),
            'created_at': ('timestamp with time zone', 'NO'),
            'updated_at': ('timestamp with time zone', 'NO'),
        }
        
        all_match = True
        for col_name, (expected_type, expected_nullable) in expected_columns.items():
            if col_name not in db_columns:
                print(f"  ✗ Missing column: {col_name}")
                all_match = False
            else:
                db_type, db_nullable = db_columns[col_name]
                # Normalize type comparison
                if 'varying' in expected_type:
                    expected_type = 'character varying'
                if 'varying' in db_type:
                    db_type = 'character varying'
                
                if expected_type not in db_type and db_type not in expected_type:
                    print(f"  ✗ Type mismatch for {col_name}: expected {expected_type}, got {db_type}")
                    all_match = False
                elif expected_nullable != db_nullable:
                    print(f"  ⚠ Nullable mismatch for {col_name}: expected {expected_nullable}, got {db_nullable}")
                else:
                    print(f"  ✓ {col_name}: {db_type} ({db_nullable})")
        
        # Verify reservations table
        print("\nVerifying reservations table:")
        result = await db.execute(text(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = :schema_name AND table_name = 'reservations'
            ORDER BY ordinal_position
        """), {"schema_name": schema_name})
        
        db_columns = {row[0]: (row[1], row[2]) for row in result.fetchall()}
        
        # Expected columns from Reservation model
        expected_columns = {
            'id': ('integer', 'NO'),
            'user_id': ('integer', 'NO'),
            'space_id': ('integer', 'NO'),
            'start_time': ('timestamp with time zone', 'NO'),
            'end_time': ('timestamp with time zone', 'NO'),
            'total_price': ('numeric', 'NO'),
            'status': ('character varying', 'NO'),
            'notes': ('text', 'YES'),
            'created_at': ('timestamp with time zone', 'NO'),
            'updated_at': ('timestamp with time zone', 'NO'),
        }
        
        for col_name, (expected_type, expected_nullable) in expected_columns.items():
            if col_name not in db_columns:
                print(f"  ✗ Missing column: {col_name}")
                all_match = False
            else:
                db_type, db_nullable = db_columns[col_name]
                # Normalize type comparison
                if 'varying' in expected_type:
                    expected_type = 'character varying'
                if 'varying' in db_type:
                    db_type = 'character varying'
                
                if expected_type not in db_type and db_type not in expected_type:
                    print(f"  ✗ Type mismatch for {col_name}: expected {expected_type}, got {db_type}")
                    all_match = False
                elif expected_nullable != db_nullable:
                    print(f"  ⚠ Nullable mismatch for {col_name}: expected {expected_nullable}, got {db_nullable}")
                else:
                    print(f"  ✓ {col_name}: {db_type} ({db_nullable})")
        
        # Verify indexes
        print("\nVerifying indexes:")
        result = await db.execute(text(f"""
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = :schema_name
            AND tablename IN ('spaces', 'reservations')
            ORDER BY tablename, indexname
        """), {"schema_name": schema_name})
        
        indexes = [row[0] for row in result.fetchall()]
        print(f"  Found {len(indexes)} indexes:")
        for idx in indexes:
            print(f"    - {idx}")
        
        # Verify foreign keys
        print("\nVerifying foreign keys:")
        result = await db.execute(text(f"""
            SELECT constraint_name, table_name
            FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
            AND table_schema = :schema_name
            AND table_name = 'reservations'
        """), {"schema_name": schema_name})
        
        fks = result.fetchall()
        if fks:
            for fk in fks:
                print(f"  ✓ {fk[1]}.{fk[0]}")
        else:
            print("  ✗ No foreign keys found")
            all_match = False
        
        print("\n=== Verification Complete ===")
        if all_match:
            print("✓ All tables are aligned with SQLAlchemy models!")
        else:
            print("✗ Some issues found. Please review above.")


if __name__ == "__main__":
    asyncio.run(verify_alignment())

