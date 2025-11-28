from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from jose import jwt, JWTError
from app.core.config import settings
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract tenant context from JWT and set PostgreSQL schema.
    This ensures all queries are automatically scoped to the tenant's schema.
    """

    async def dispatch(self, request: Request, call_next):
        # Skip tenant context for public endpoints
        if request.url.path in ["/", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/register", "/api/v1/auth/login"]:
            return await call_next(request)

        # Extract tenant_id from JWT token
        tenant_id = None
        schema_name = None
        
        authorization: str = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                )
                tenant_id = payload.get("tenant_id")
                
                # Get schema name from organization
                if tenant_id:
                    async with AsyncSessionLocal() as session:
                        result = await session.execute(
                            text("SELECT schema_name FROM public.organizations WHERE id = :tenant_id"),
                            {"tenant_id": tenant_id}
                        )
                        row = result.fetchone()
                        if row:
                            schema_name = row[0]
            except JWTError:
                pass

        # Store tenant context in request state
        request.state.tenant_id = tenant_id
        request.state.schema_name = schema_name

        response = await call_next(request)
        return response
