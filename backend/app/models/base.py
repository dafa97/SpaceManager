from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


def get_utc_now():
    """Get current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """Base model with common fields for all tables."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False
    )
