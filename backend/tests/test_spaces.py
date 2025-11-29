import pytest
from httpx import AsyncClient
from app.models.space import SpaceType

@pytest.mark.asyncio
async def test_create_space(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/v1/spaces",
        json={
            "name": "Test Space",
            "description": "A test space",
            "space_type": "hourly",
            "price_per_unit": 100.0,
            "capacity": 10,
            "is_available": True
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Space"
    assert data["space_type"] == "hourly"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_spaces(client: AsyncClient, auth_headers: dict):
    # Create a space first
    await client.post(
        "/api/v1/spaces",
        json={
            "name": "Space 1",
            "space_type": "daily",
            "price_per_unit": 50.0
        },
        headers=auth_headers
    )
    
    response = await client.get("/api/v1/spaces", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(s["name"] == "Space 1" for s in data)

@pytest.mark.asyncio
async def test_get_space(client: AsyncClient, auth_headers: dict):
    # Create a space
    create_res = await client.post(
        "/api/v1/spaces",
        json={
            "name": "Space to Get",
            "space_type": "monthly",
            "price_per_unit": 1000.0
        },
        headers=auth_headers
    )
    space_id = create_res.json()["id"]
    
    response = await client.get(f"/api/v1/spaces/{space_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == space_id
    assert data["name"] == "Space to Get"

@pytest.mark.asyncio
async def test_update_space(client: AsyncClient, auth_headers: dict):
    # Create a space
    create_res = await client.post(
        "/api/v1/spaces",
        json={
            "name": "Space to Update",
            "space_type": "hourly",
            "price_per_unit": 10.0
        },
        headers=auth_headers
    )
    space_id = create_res.json()["id"]
    
    # Update it
    response = await client.put(
        f"/api/v1/spaces/{space_id}",
        json={
            "name": "Updated Space Name",
            "price_per_unit": 20.0
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Space Name"
    assert data["price_per_unit"] == 20.0
    
    # Verify update
    get_res = await client.get(f"/api/v1/spaces/{space_id}", headers=auth_headers)
    assert get_res.json()["name"] == "Updated Space Name"

@pytest.mark.asyncio
async def test_delete_space(client: AsyncClient, auth_headers: dict):
    # Create a space
    create_res = await client.post(
        "/api/v1/spaces",
        json={
            "name": "Space to Delete",
            "space_type": "hourly",
            "price_per_unit": 10.0
        },
        headers=auth_headers
    )
    space_id = create_res.json()["id"]
    
    # Delete it
    response = await client.delete(f"/api/v1/spaces/{space_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify deletion
    get_res = await client.get(f"/api/v1/spaces/{space_id}", headers=auth_headers)
    assert get_res.status_code == 404
