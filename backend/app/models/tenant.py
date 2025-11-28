from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel


class Organization(BaseModel):
    """
    Organization/Tenant model.
    Each organization represents a separate tenant with isolated data.
    Stored in the public schema.
    """
    __tablename__ = "organizations"
    __table_args__ = {"schema": "public"}

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    schema_name: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Contact information
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # Relationships
    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship("OrganizationMember", back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
