from datetime import datetime
from pydantic import BaseModel, EmailStr

class OrganizationBase(BaseModel):
    name: str
    slug: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationMemberResponse(BaseModel):
    organization: OrganizationResponse
    role: str
    status: str
    created_at: datetime  # Changed from joined_at

    class Config:
        from_attributes = True

class InviteUserRequest(BaseModel):
    email: EmailStr
    role: str = "MEMBER"
