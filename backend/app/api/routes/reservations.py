from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db
from app.models.user import User
from app.models.reservation import Reservation, ReservationStatus
from app.models.space import Space
from app.schemas.reservation import ReservationCreate, ReservationUpdate, ReservationResponse
from app.api.dependencies.auth import get_current_active_user
from typing import List
from datetime import datetime

router = APIRouter()


async def set_tenant_schema(db: AsyncSession, user: User):
    """Helper to set the search path to tenant schema."""
    # user.tenant_id es inyectado por la dependencia de autenticación
    result = await db.execute(
        text("SELECT schema_name FROM public.organizations WHERE id = :org_id"),
        {"org_id": user.tenant_id}
    )
    row = result.fetchone()
    if row:
        schema_name = row[0]
        await db.execute(text(f"SET search_path TO {schema_name}, public"))


async def calculate_price(
    db: AsyncSession,
    space_id: int,
    start_time: datetime,
    end_time: datetime
) -> float:
    """Calculate reservation price based on space type and duration."""
    result = await db.execute(
        select(Space).where(Space.id == space_id)
    )
    space = result.scalar_one_or_none()
    
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )
    
    # Calculate duration
    duration = end_time - start_time
    
    # Calculate price based on space type
    if space.space_type == "hourly":
        hours = duration.total_seconds() / 3600
        total_price = hours * float(space.price_per_unit)
    elif space.space_type == "daily":
        days = duration.days or 1
        total_price = days * float(space.price_per_unit)
    else:  # monthly
        # Approximate months (30 days)
        months = max(1, duration.days // 30)
        total_price = months * float(space.price_per_unit)
    
    return round(total_price, 2)


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation_data: ReservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Reservation:
    """Create a new reservation."""
    await set_tenant_schema(db, current_user)
    
    # Check if space exists and is available
    result = await db.execute(
        select(Space).where(Space.id == reservation_data.space_id)
    )
    space = result.scalar_one_or_none()
    
    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Space not found"
        )
    
    if not space.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Space is not available"
        )
    
    # Calculate price
    total_price = await calculate_price(
        db,
        reservation_data.space_id,
        reservation_data.start_time,
        reservation_data.end_time
    )
    
    # Create reservation
    reservation = Reservation(
        **reservation_data.model_dump(),
        user_id=current_user.id,
        total_price=total_price,
        status=ReservationStatus.PENDING
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    
    return reservation


@router.get("/", response_model=List[ReservationResponse])
async def list_reservations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[Reservation]:
    """List all reservations for the current user."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Reservation)
        .where(Reservation.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    reservations = result.scalars().all()
    
    return list(reservations)


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Reservation:
    """Get a specific reservation."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Reservation)
        .where(Reservation.id == reservation_id)
        .where(Reservation.user_id == current_user.id)
    )
    reservation = result.scalar_one_or_none()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    return reservation


@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: int,
    reservation_data: ReservationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Reservation:
    """Update a reservation."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Reservation)
        .where(Reservation.id == reservation_id)
        .where(Reservation.user_id == current_user.id)
    )
    reservation = result.scalar_one_or_none()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    # Update fields
    update_data = reservation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reservation, field, value)
    
    await db.commit()
    await db.refresh(reservation)
    
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Cancel a reservation (soft delete by setting status to cancelled)."""
    await set_tenant_schema(db, current_user)
    
    result = await db.execute(
        select(Reservation)
        .where(Reservation.id == reservation_id)
        .where(Reservation.user_id == current_user.id)
    )
    reservation = result.scalar_one_or_none()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    reservation.status = ReservationStatus.CANCELLED
    await db.commit()
