from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Token(BaseModel):
    """
    Token model for storing refresh tokens.
    Allows for token revocation.
    """
    __tablename__ = "tokens"
    __table_args__ = {"schema": "public"}

    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    token_type: Mapped[str] = mapped_column(String(50), nullable=False, default="refresh")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("public.users.id"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tokens")

    def __repr__(self) -> str:
        return f"<Token(id={self.id}, user_id={self.user_id}, type={self.token_type})>"
