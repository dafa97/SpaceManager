"""fix_tenant_tables_remove_public

Revision ID: 9d52e7d39b12
Revises: 06f9a76e8661
Create Date: 2025-11-30 11:40:49.825043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d52e7d39b12'
down_revision: Union[str, None] = '06f9a76e8661'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove spaces and reservations tables from public schema if they exist
    # These tables should only exist in tenant-specific schemas
    op.execute("DROP TABLE IF EXISTS public.reservations CASCADE")
    op.execute("DROP TABLE IF EXISTS public.spaces CASCADE")
    
    # Also drop any enum types that might have been created in public schema
    # (though we're using VARCHAR now instead of enums)
    op.execute("DROP TYPE IF EXISTS reservation_status CASCADE")
    op.execute("DROP TYPE IF EXISTS space_type CASCADE")


def downgrade() -> None:
    # Note: We cannot easily recreate these tables in downgrade
    # because we don't know their original structure
    # In practice, this migration should not be rolled back
    pass
