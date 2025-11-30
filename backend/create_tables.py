import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def create_tables():
    async with AsyncSessionLocal() as session:
        # Create users table if not exists
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS public.users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create organizations table if not exists
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS public.organizations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(100) NOT NULL UNIQUE,
                schema_name VARCHAR(63) NOT NULL UNIQUE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                email VARCHAR(255),
                phone VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create organization_members table if not exists
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS public.organization_members (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                organization_id INTEGER NOT NULL,
                role VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES public.users (id),
                FOREIGN KEY (organization_id) REFERENCES public.organizations (id)
            )
        """))

        # Create tokens table if not exists
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS public.tokens (
                id SERIAL PRIMARY KEY,
                token VARCHAR(512) NOT NULL UNIQUE,
                token_type VARCHAR(50) NOT NULL,
                user_id INTEGER NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES public.users (id)
            )
        """))

        # Create indexes
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_users_email ON public.users (email)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_users_id ON public.users (id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_organizations_id ON public.organizations (id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_organizations_name ON public.organizations (name)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_organizations_slug ON public.organizations (slug)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_organization_members_id ON public.organization_members (id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_organization_members_organization_id ON public.organization_members (organization_id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_organization_members_user_id ON public.organization_members (user_id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_tokens_id ON public.tokens (id)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_tokens_token ON public.tokens (token)"))
        await session.execute(text("CREATE INDEX IF NOT EXISTS ix_public_tokens_user_id ON public.tokens (user_id)"))

        await session.commit()
        print("Tables created successfully")

if __name__ == "__main__":
    asyncio.run(create_tables())
