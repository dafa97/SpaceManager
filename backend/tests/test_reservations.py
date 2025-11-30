import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_reservation(client: AsyncClient, auth_headers):
    # Crear un espacio primero
    space_data = {
        "name": "Sala Reuniones",
        "description": "Sala para juntas",
        "space_type": "hourly",
        "price_per_unit": 50.0,
        "capacity": 5,
        "is_available": True
    }
    space_resp = await client.post("/api/v1/spaces", json=space_data, headers=auth_headers)
    assert space_resp.status_code == 201
    space_id = space_resp.json()["id"]

    # Crear una reservación
    reservation_data = {
        "space_id": space_id,
        "start_time": "2025-12-01T10:00:00Z",
        "end_time": "2025-12-01T12:00:00Z",
        "notes": "Reunión de equipo"
    }
    response = await client.post("/api/v1/reservations", json=reservation_data, headers=auth_headers)
    assert response.status_code == 201
    res = response.json()
    assert res["space_id"] == space_id
    assert res["notes"] == "Reunión de equipo"

@pytest.mark.asyncio
async def test_list_reservations(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/reservations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_reservation(client: AsyncClient, auth_headers):
    # Crear un espacio y una reservación
    space_data = {
        "name": "Oficina Privada",
        "description": "Oficina para 2 personas",
        "space_type": "hourly",
        "price_per_unit": 80.0,
        "capacity": 2,
        "is_available": True
    }
    space_resp = await client.post("/api/v1/spaces", json=space_data, headers=auth_headers)
    space_id = space_resp.json()["id"]
    reservation_data = {
        "space_id": space_id,
        "start_time": "2025-12-02T09:00:00Z",
        "end_time": "2025-12-02T11:00:00Z"
    }
    res_resp = await client.post("/api/v1/reservations", json=reservation_data, headers=auth_headers)
    reservation_id = res_resp.json()["id"]

    # Obtener la reservación
    response = await client.get(f"/api/v1/reservations/{reservation_id}", headers=auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["id"] == reservation_id
    assert res["space_id"] == space_id

@pytest.mark.asyncio
async def test_update_reservation(client: AsyncClient, auth_headers):
    # Crear un espacio y una reservación
    space_data = {
        "name": "Coworking",
        "description": "Espacio abierto",
        "space_type": "hourly",
        "price_per_unit": 30.0,
        "capacity": 10,
        "is_available": True
    }
    space_resp = await client.post("/api/v1/spaces", json=space_data, headers=auth_headers)
    space_id = space_resp.json()["id"]
    reservation_data = {
        "space_id": space_id,
        "start_time": "2025-12-03T14:00:00Z",
        "end_time": "2025-12-03T16:00:00Z"
    }
    res_resp = await client.post("/api/v1/reservations", json=reservation_data, headers=auth_headers)
    reservation_id = res_resp.json()["id"]

    # Actualizar la reservación
    update_data = {
        "notes": "Cambio de horario",
        "end_time": "2025-12-03T17:00:00Z"
    }
    response = await client.put(f"/api/v1/reservations/{reservation_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    res = response.json()
    assert res["notes"] == "Cambio de horario"
    assert res["end_time"].startswith("2025-12-03T17:00:00")

@pytest.mark.asyncio
async def test_delete_reservation(client: AsyncClient, auth_headers):
    # Crear un espacio y una reservación
    space_data = {
        "name": "Sala Creativa",
        "description": "Para talleres",
        "space_type": "hourly",
        "price_per_unit": 60.0,
        "capacity": 8,
        "is_available": True
    }
    space_resp = await client.post("/api/v1/spaces", json=space_data, headers=auth_headers)
    space_id = space_resp.json()["id"]
    reservation_data = {
        "space_id": space_id,
        "start_time": "2025-12-04T10:00:00Z",
        "end_time": "2025-12-04T12:00:00Z"
    }
    res_resp = await client.post("/api/v1/reservations", json=reservation_data, headers=auth_headers)
    reservation_id = res_resp.json()["id"]

    # Eliminar la reservación
    response = await client.delete(f"/api/v1/reservations/{reservation_id}", headers=auth_headers)
    assert response.status_code == 204
    # Verificar que el status es cancelled (soft delete)
    get_resp = await client.get(f"/api/v1/reservations/{reservation_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    res = get_resp.json()
    assert res["status"] == "cancelled"
