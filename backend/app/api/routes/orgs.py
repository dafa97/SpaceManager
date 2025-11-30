from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.tenant import Organization
from app.models.member import OrganizationMember
from app.schemas.org import OrganizationCreate, OrganizationResponse, OrganizationMemberResponse, InviteUserRequest
from app.api.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=list[OrganizationMemberResponse])
async def list_organizations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[OrganizationMemberResponse]:
    """
    List organizations the current user belongs to.
    """
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .options(selectinload(OrganizationMember.organization))
    )
    memberships = result.scalars().all()
    return memberships

@router.post("/", response_model=OrganizationMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationMemberResponse:
    """
    Create a new organization.
    """
    # Check if slug is taken
    result = await db.execute(
        select(Organization).where(Organization.slug == org_data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization slug already taken"
        )
    
    # Create organization
    schema_name = f"tenant_{org_data.slug.replace('-', '_')}"
    organization = Organization(
        name=org_data.name,
        slug=org_data.slug,
        schema_name=schema_name,
        is_active=True
    )
    db.add(organization)
    await db.flush()
    
    # Create tenant schema
    await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
    
    # Create membership (OWNER)
    member = OrganizationMember(
        user_id=current_user.id,
        organization_id=organization.id,
        role="OWNER",
        status="ACTIVE"
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    return member

@router.get("/{slug}", response_model=OrganizationResponse)
async def get_organization_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """
    Get organization by slug.
    """
    # Check if user is a member of this organization
    result = await db.execute(
        select(Organization)
        .join(OrganizationMember)
        .where(Organization.slug == slug)
        .where(OrganizationMember.user_id == current_user.id)
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization

@router.post("/{org_id}/invite", status_code=status.HTTP_200_OK)
async def invite_user(
    org_id: int,
    invite_data: InviteUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Invite a user to the organization.
    """
    # Check permissions
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.role.in_(["OWNER", "ADMIN"]))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
        
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == invite_data.email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Check if already a member
        result = await db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.user_id == user.id)
            .where(OrganizationMember.organization_id == org_id)
        )
        if result.scalar_one_or_none():
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member"
            )
            
        # Add as member
        member = OrganizationMember(
            user_id=user.id,
            organization_id=org_id,
            role=invite_data.role,
            status="ACTIVE" # Auto-join for now if user exists
        )
        db.add(member)
        await db.commit()
        return {"message": "User added to organization"}
    else:
        # TODO: Implement invitation flow for non-existing users (send email)
        # For now, we'll just return a message
        return {"message": "Invitation sent (simulated)"}
