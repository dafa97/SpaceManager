from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db
from app.models.user import User
from app.models.space import Space
from app.schemas.space import SpaceCreate, SpaceUpdate, SpaceResponse
from app.api.dependencies.auth import get_current_active_user
from typing import List

router = APIRouter()


async def set_tenant_schema(db: AsyncSession, user: User):
    """Helper to set the search path to tenant schema."""
    # user.tenant_id is injected by get_current_user dependency
    result = await db.execute(
        text("SELECT schema_name FROM public.organizations WHERE id = :org_id"),
        {"org_id": user.tenant_id}
    )
    row = result.fetchone()
    if row:
        schema_name = row[0]
        await db.execute(text(f"SET search_path TO {schema_name}, public"))


@router.post("/", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
async def create_space(
    space_data: SpaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Space:
    """Create a new space in the current tenant."""
    await set_tenant_schema(db, current_user)
    
    space = Space(**space_data.model_dump())
    db.add(space)
    await db.commit()
    await db.refresh(space)
    
    return space


@router.get("/", response_model=List[SpaceResponse])
async def list_spaces(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Space]:
    """List all spaces for the current tenant."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Space).offset(skip).limit(limit)
    )
    spaces = result.scalars().all()
    
    return list(spaces)


@router.get("/{space_id}", response_model=SpaceResponse)
async def get_space(
    space_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Space:
    """Get a specific space by ID."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Space).where(Space.id == space_id)
    )
    space = result.scalar_one_or_none()
    
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )
    
    return space


@router.put("/{space_id}", response_model=SpaceResponse)
async def update_space(
    space_id: int,
    space_data: SpaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Space:
    """Update a space."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Space).where(Space.id == space_id)
    )
    space = result.scalar_one_or_none()
    
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )
    
    # Update fields
    update_data = space_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(space, field, value)
    
    await db.commit()
    await db.refresh(space)
    
    return space


@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_space(
    space_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a space."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Space).where(Space.id == space_id)
    )
    space = result.scalar_one_or_none()
    
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )
    
    await db.delete(space)
    await db.commit()
