from datetime import datetime
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class BaseModel(Base):
    """Base model with common fields for all tables."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
