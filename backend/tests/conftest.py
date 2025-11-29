import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
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

engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)
TestingSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

# pytest-asyncio configuration
pytestmark = pytest.mark.asyncio

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        # Cleanup: rollback any uncommitted changes
        await session.rollback()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as c:
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
    await db_session.flush()  # Flush instead of commit to avoid transaction issues
    await db_session.refresh(org)
    
    # Create the schema using the same session
    await db_session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    await db_session.flush()
    
    # Create tables in the schema
    # Use a raw connection from the engine to set search path and create tables
    async with engine.connect() as conn:
        await conn.execute(text(f"SET search_path TO {schema_name}, public"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
    
    # Finally commit the organization
    await db_session.commit()
    
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
