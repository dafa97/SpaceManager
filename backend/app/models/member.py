from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class OrganizationMember(BaseModel):
    """
    Association table between User and Organization.
    Stores the role of the user in the organization.
    """
    __tablename__ = "organization_members"
    __table_args__ = {"schema": "public"}

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("public.users.id"), nullable=False, index=True
    )
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("public.organizations.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="MEMBER")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE") # ACTIVE, INVITED
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="memberships")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")

    def __repr__(self) -> str:
        return f"<OrganizationMember(user_id={self.user_id}, org_id={self.organization_id}, role={self.role})>"
