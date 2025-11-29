import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.main import app
from app.core.config import settings
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.tenant import Organization
from app.models.user import User
from app.models.member import OrganizationMember

# Use a separate test database or the same one?
# Ideally a separate one, but for now let's use the same one but with a test schema.
# Actually, the app uses schemas for tenants, so we can just create a test tenant.
# But we need to make sure we don't pollute the public schema too much.
# For simplicity in this environment, I'll use the existing DB but be careful.

# Override the engine to use the same URL (or a test one if available)
# In a real scenario, we'd use a separate test DB.
TEST_DATABASE_URL = str(settings.DATABASE_URL)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        # Rollback is handled by the fact that we don't commit in tests usually,
        # or we can explicitly rollback here.
        await session.rollback()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    # Create a unique test organization
    import uuid
    slug = f"test_org_{uuid.uuid4().hex[:8]}"
    schema_name = f"tenant_{slug}"
    
    org = Organization(
        name="Test Organization",
        slug=slug,
        schema_name=schema_name,
        is_active=True
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)
    
    # Create the schema
    await db_session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    await db_session.commit()
    
    # Create tables in the schema
    # We need to create the tables for the tenant models.
    # This is tricky because we need to bind the engine to the schema or use the metadata.
    # For now, let's assume the app handles table creation or we do it manually for Space.
    # The Space model is defined in app.models.space.
    # We can use `Base.metadata.create_all` but we need to specify the schema.
    
    # Actually, the app uses Alembic for migrations.
    # For tests, we can just create the specific table we need.
    from app.models.space import Space
    
    async with engine.begin() as conn:
        # We need to set the search path to the tenant schema to create tables there?
        # Or we can just use the table name with schema?
        # SQLAlchemy models usually don't have schema hardcoded.
        # The TenantMiddleware sets the search path.
        
        # Let's try setting the search path and creating tables.
        await conn.execute(text(f"SET search_path TO {schema_name}, public"))
        await conn.run_sync(Base.metadata.create_all)
        
    return org

@pytest.fixture
async def test_user(db_session: AsyncSession, test_org: Organization) -> User:
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    user = User(
        email=email,
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    member = OrganizationMember(
        user_id=user.id,
        organization_id=test_org.id,
        role="OWNER",
        status="ACTIVE"
    )
    db_session.add(member)
    await db_session.commit()
    
    return user

@pytest.fixture
async def auth_headers(test_user: User, test_org: Organization) -> dict:
    token = create_access_token(subject=test_user.id, tenant_id=test_org.id)
    return {"Authorization": f"Bearer {token}"}
