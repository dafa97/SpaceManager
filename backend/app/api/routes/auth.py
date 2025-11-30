from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from app.models.user import User
from app.models.tenant import Organization
from app.models.member import OrganizationMember
from app.models.token import Token as RefreshTokenModel
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserResponse
from app.api.dependencies.auth import get_current_user

class RefreshTokenRequest(BaseModel):
    refresh_token: str

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Register a new user and organization.
    Creates a new tenant schema for the organization.
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if organization slug is taken
    result = await db.execute(
        select(Organization).where(Organization.slug == user_data.organization_slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already taken"
        )
    
    # Create organization
    schema_name = f"tenant_{user_data.organization_slug.replace('-', '_')}"
    organization = Organization(
        name=user_data.organization_name,
        slug=user_data.organization_slug,
        schema_name=schema_name,
        is_active=True
    )
    db.add(organization)
    await db.flush()
    
    # Create tenant schema
    await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

    # Create enum type for space_type in tenant schema
    await db.execute(text(f"""
        DO $$ BEGIN
            CREATE TYPE {schema_name}.space_type AS ENUM ('hourly', 'daily', 'monthly');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Create spaces table in tenant schema
    await db.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.spaces (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            space_type {schema_name}.space_type NOT NULL,
            capacity INTEGER,
            price_per_unit NUMERIC(10, 2) NOT NULL,
            is_available BOOLEAN NOT NULL DEFAULT TRUE,
            floor VARCHAR(50),
            area_sqm NUMERIC(10, 2),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Create indexes for spaces table
    await db.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_spaces_id ON {schema_name}.spaces (id)"))
    await db.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_spaces_name ON {schema_name}.spaces (name)"))
    await db.execute(text(f"CREATE INDEX IF NOT EXISTS ix_{schema_name.replace('.', '_')}_spaces_space_type ON {schema_name}.spaces (space_type)"))

    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=True 
    )
    db.add(user)
    await db.flush()

    # Create membership (OWNER)
    member = OrganizationMember(
        user_id=user.id,
        organization_id=organization.id,
        role="OWNER",
        status="ACTIVE"
    )
    db.add(member)
    await db.commit()
    await db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(
        subject=user.id,
        tenant_id=organization.id
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    # Store refresh token
    db_token = RefreshTokenModel(
        token=refresh_token,
        token_type="refresh",
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7) # Hardcoded for now, should use settings
    )
    db.add(db_token)
    await db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login with email and password.
    Returns JWT token with user and tenant information.
    """
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Get user's default organization (first one for now)
    # In future, we might let user choose or store last used org
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id)
        .where(OrganizationMember.status == "ACTIVE")
        .limit(1)
    )
    member = result.scalar_one_or_none()
    
    if not member:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no active organization memberships"
        )

    # Create tokens
    access_token = create_access_token(
        subject=user.id,
        tenant_id=member.organization_id
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    # Store refresh token
    db_token = RefreshTokenModel(
        token=refresh_token,
        token_type="refresh",
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_token)
    await db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user information.
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    request_body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Refresh access token using refresh token.
    """
    refresh_token = request_body.refresh_token
    
    # In a real app, verify the refresh token signature and check against DB
    # For now, we'll assume it's valid if it exists in DB and is not expired
    
    result = await db.execute(
        select(RefreshTokenModel)
        .where(RefreshTokenModel.token == refresh_token)
        .where(RefreshTokenModel.is_revoked == False)
    )
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
        
    if db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
        
    # Get user
    result = await db.execute(
        select(User).where(User.id == db_token.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    # Get active membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id)
        .where(OrganizationMember.status == "ACTIVE")
        .limit(1)
    )
    member = result.scalar_one_or_none()
    
    if not member:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no active organization memberships"
        )

    # Create new tokens
    access_token = create_access_token(
        subject=user.id,
        tenant_id=member.organization_id
    )
    new_refresh_token = create_refresh_token(subject=user.id)
    
    # Revoke old token
    db_token.is_revoked = True
    
    # Store new refresh token
    new_db_token = RefreshTokenModel(
        token=new_refresh_token,
        token_type="refresh",
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(new_db_token)
    await db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )
