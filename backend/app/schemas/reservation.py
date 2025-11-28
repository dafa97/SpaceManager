from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from app.models.reservation import ReservationStatus


class ReservationBase(BaseModel):
    """Base reservation schema."""
    space_id: int
    start_time: datetime
    end_time: datetime
    notes: str | None = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: datetime, info) -> datetime:
        """Validate that end_time is after start_time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ReservationCreate(ReservationBase):
    """Reservation creation schema."""
    pass


class ReservationUpdate(BaseModel):
    """Reservation update schema."""
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: ReservationStatus | None = None
    notes: str | None = None


class ReservationResponse(ReservationBase):
    """Reservation response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    total_price: float
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime
