import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    data = {
        "email": "newuser@example.com",
        "password": "testpassword",
        "full_name": "Nuevo Usuario",
        "organization_name": "Org Test",
        "organization_slug": "org-test"
    }
    response = await client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 201
    res = response.json()
    assert "access_token" in res
    assert "refresh_token" in res
    assert res["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login(client: AsyncClient, test_user, test_org):
    data = {
        "email": test_user.email,
        "password": "hashed_password"  # Debe coincidir con el valor en el fixture
    }
    response = await client.post("/api/v1/auth/login", json=data)
    assert response.status_code == 200
    res = response.json()
    assert "access_token" in res
    assert res["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_auth_me(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["email"].endswith("@example.com")
    assert res["is_active"] is True
