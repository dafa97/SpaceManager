from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
import enum


class ReservationStatus(str, enum.Enum):
    """Status of a reservation."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Reservation(BaseModel):
    """
    Reservation model for space bookings.
    Stored in tenant-specific schema.
    """
    __tablename__ = "reservations"

    # Foreign keys (user_id references public.users)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    space_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("spaces.id"), nullable=False, index=True
    )
    
    # Time slots
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    
    # Pricing
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Status
    status: Mapped[ReservationStatus] = mapped_column(
        SQLEnum(ReservationStatus, name="reservation_status"),
        default=ReservationStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Optional notes
    notes: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<Reservation(id={self.id}, space_id={self.space_id}, status={self.status})>"
