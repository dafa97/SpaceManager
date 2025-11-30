from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
import enum


class SpaceType(str, enum.Enum):
    """Types of rental spaces."""
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"


class Space(BaseModel):
    """
    Space/Room model for rental units.
    Stored in tenant-specific schema.
    """
    __tablename__ = "spaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    # Use String instead of SQLEnum to avoid issues with tenant-specific enum types
    # The enum validation is still enforced at the Pydantic schema level
    space_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    
    # Capacity and pricing
    capacity: Mapped[int] = mapped_column(Integer, nullable=True)
    price_per_unit: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Availability
    is_available: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Optional metadata
    floor: Mapped[str] = mapped_column(String(50), nullable=True)
    area_sqm: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)

    def __repr__(self) -> str:
        return f"<Space(id={self.id}, name={self.name}, type={self.space_type})>"
