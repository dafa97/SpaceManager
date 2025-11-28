from sqlalchemy import String, Numeric, Integer, Enum as SQLEnum
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
    space_type: Mapped[SpaceType] = mapped_column(
        SQLEnum(SpaceType, name="space_type"), nullable=False, index=True
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
