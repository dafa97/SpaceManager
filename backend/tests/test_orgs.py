import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_org_and_list(client: AsyncClient):
    # Registro de usuario y organización
    data = {
        "email": "orguser@example.com",
        "password": "testpassword",
        "full_name": "Org User",
        "organization_name": "Org Nueva",
        "organization_slug": "org-nueva"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Listar organizaciones (debería incluir la nueva)
    resp = await client.get("/api/v1/orgs", headers=headers)
    assert resp.status_code == 200
    orgs = resp.json()
    assert any(o["organization"]["slug"] == "org-nueva" for o in orgs)

@pytest.mark.asyncio
async def test_get_org_by_slug(client: AsyncClient, auth_headers):
    # Crear una organización adicional
    data = {
        "email": "otro@example.com",
        "password": "testpassword",
        "full_name": "Otro User",
        "organization_name": "Org Extra",
        "organization_slug": "org-extra"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=data)
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Depuración: listar organizaciones del usuario
    list_resp = await client.get("/api/v1/orgs", headers=headers)
    print("ORGS LIST:", list_resp.status_code, list_resp.json())
    # Obtener la organización por slug
    resp = await client.get("/api/v1/orgs/org-extra", headers=headers)
    print("ORG BY SLUG:", resp.status_code, resp.text)
    assert resp.status_code == 200
    org = resp.json()
    assert org["slug"] == "org-extra"
    assert org["name"] == "Org Extra"
