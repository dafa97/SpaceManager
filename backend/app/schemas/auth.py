from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: int
    tenant_id: int


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str
    full_name: str | None = None
    organization_name: str
    organization_slug: str
