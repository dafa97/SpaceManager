from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    slug: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationMemberResponse(BaseModel):
    organization: OrganizationResponse
    role: str
    status: str
    created_at: datetime  # Changed from joined_at

    model_config = ConfigDict(from_attributes=True)

class InviteUserRequest(BaseModel):
    email: EmailStr
    role: str = "MEMBER"
