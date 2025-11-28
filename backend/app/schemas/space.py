from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.space import SpaceType


class SpaceBase(BaseModel):
    """Base space schema."""
    name: str
    description: str | None = None
    space_type: SpaceType
    capacity: int | None = None
    price_per_unit: float
    is_available: bool = True
    floor: str | None = None
    area_sqm: float | None = None


class SpaceCreate(SpaceBase):
    """Space creation schema."""
    pass


class SpaceUpdate(BaseModel):
    """Space update schema."""
    name: str | None = None
    description: str | None = None
    space_type: SpaceType | None = None
    capacity: int | None = None
    price_per_unit: float | None = None
    is_available: bool | None = None
    floor: str | None = None
    area_sqm: float | None = None


class SpaceResponse(SpaceBase):
    """Space response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
