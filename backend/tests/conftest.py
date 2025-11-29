import pytest
import uuid
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from app.main import app
from app.core.config import settings
from app.core.database import get_db, Base, AsyncSessionLocal
from app.core.security import create_access_token
from app.models.tenant import Organization
from app.models.user import User
from app.models.member import OrganizationMember
from app.middleware.tenant import TenantMiddleware

# Use the same test database URL
TEST_DATABASE_URL = str(settings.DATABASE_URL)

# Store the test session factory for middleware to use
_test_session_factory = None

@pytest.fixture
async def engine():
    """Create test database engine."""
    _engine = create_async_engine(
        TEST_DATABASE_URL, 
        echo=False, 
        pool_pre_ping=True
    )
    
    # Create public schema tables
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield _engine
    
    # Cleanup
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await _engine.dispose()

@pytest.fixture
async def session_factory(engine):
    """Create async session factory."""
    global _test_session_factory
    _test_session_factory = async_sessionmaker(
        engine, 
        expire_on_commit=False, 
        class_=AsyncSession
    )
    return _test_session_factory

@pytest.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for each test."""
    async with session_factory() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session: AsyncSession, engine) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTP client for testing."""
    # Override the get_db dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # Store test session in app state for middleware to use
    app.test_session = db_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as c:
        yield c
    
    app.dependency_overrides.clear()
    # Clean up
    if hasattr(app, "test_session"):
        delattr(app, "test_session")

@pytest.fixture
async def test_org(db_session: AsyncSession, engine) -> AsyncGenerator[Organization, None]:
    """Create a test organization with its own schema."""
    slug = f"test_org_{uuid.uuid4().hex[:8]}"
    schema_name = f"tenant_{slug}"
    
    # Create organization in public schema
    org = Organization(
        name="Test Organization",
        slug=slug,
        schema_name=schema_name,
        is_active=True
    )
    db_session.add(org)
    await db_session.flush()
    
    # Create the tenant schema
    await db_session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    await db_session.commit()
    await db_session.refresh(org)
    
    # Create tables in the tenant schema using a fresh connection
    async with engine.connect() as conn:
        await conn.execute(text(f"SET search_path TO {schema_name}, public"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
    
    yield org
    
    # Cleanup
    try:
        async with engine.connect() as conn:
            await conn.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
            await conn.commit()
    except Exception:
        pass  # Ignore errors on cleanup

@pytest.fixture
async def test_user(db_session: AsyncSession, test_org: Organization) -> User:
    """Create a test user."""
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    user = User(
        email=email,
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    
    # Add user to organization
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
    """Generate authorization headers with JWT token."""
    token = create_access_token(subject=test_user.id, tenant_id=test_org.id)
    return {"Authorization": f"Bearer {token}"}
