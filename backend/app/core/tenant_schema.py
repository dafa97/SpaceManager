"""
Helper functions for managing tenant schemas.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, inspect
from app.core.database import engine, Base
from app.models.space import Space
from app.models.reservation import Reservation


async def init_tenant_schema(db: AsyncSession, schema_name: str) -> None:
    """
    Initialize a tenant schema by creating the schema and all required tables.
    
    This function:
    1. Creates the schema if it doesn't exist
    2. Creates the spaces and reservations tables in the schema
    3. Creates all necessary indexes and constraints
    
    Args:
        db: Database session
        schema_name: Name of the tenant schema to initialize
    """
    # Create schema if it doesn't exist
    await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    await db.commit()
    
    # Create tables using SQLAlchemy metadata
    # We need to temporarily set the schema for Space and Reservation models
    # and then create the tables
    
    # Get the table definitions from the models
    space_table = Space.__table__
    reservation_table = Reservation.__table__
    
    # Set the schema for these tables
    space_table.schema = schema_name
    reservation_table.schema = schema_name
    
    # Create tables using raw SQL based on the model definitions
    # This ensures consistency with the models
    await _create_spaces_table(db, schema_name)
    await _create_reservations_table(db, schema_name)
    
    await db.commit()


async def _create_spaces_table(db: AsyncSession, schema_name: str) -> None:
    """Create the spaces table in the tenant schema."""
    await db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.spaces (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            space_type VARCHAR(20) NOT NULL,
            capacity INTEGER,
            price_per_unit NUMERIC(10, 2) NOT NULL,
            is_available BOOLEAN NOT NULL DEFAULT TRUE,
            floor VARCHAR(50),
            area_sqm NUMERIC(10, 2),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Create indexes
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_spaces_id 
        ON {schema_name}.spaces (id)
    """))
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_spaces_name 
        ON {schema_name}.spaces (name)
    """))
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_spaces_space_type 
        ON {schema_name}.spaces (space_type)
    """))


async def _create_reservations_table(db: AsyncSession, schema_name: str) -> None:
    """Create the reservations table in the tenant schema."""
    await db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.reservations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            space_id INTEGER NOT NULL,
            start_time TIMESTAMP WITH TIME ZONE NOT NULL,
            end_time TIMESTAMP WITH TIME ZONE NOT NULL,
            total_price NUMERIC(10, 2) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT reservations_space_id_fkey 
                FOREIGN KEY (space_id) REFERENCES {schema_name}.spaces(id)
        )
    """))
    
    # Create indexes
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_reservations_id 
        ON {schema_name}.reservations (id)
    """))
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_reservations_user_id 
        ON {schema_name}.reservations (user_id)
    """))
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_reservations_space_id 
        ON {schema_name}.reservations (space_id)
    """))
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_reservations_start_time 
        ON {schema_name}.reservations (start_time)
    """))
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_reservations_end_time 
        ON {schema_name}.reservations (end_time)
    """))
    await db.execute(text(f"""
        CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_reservations_status 
        ON {schema_name}.reservations (status)
    """))

