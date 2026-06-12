from uuid import uuid4
from tests.conftest import register_user

CAR_PAYLOAD = {
    "car_uuid": str(uuid4()),
    "name": "My BMW",
    "make": "BMW",
    "model": "M3",
    "year": 2020,
    "vin": "WBS8M9C50J5J12345",
    "mileage": 50000,
    "license_plate": "CJ01ABC",
}

def create_car(client, auth_headers):
    data = {**CAR_PAYLOAD, "car_uuid": str(uuid4())}
    return client.post("/cars/", json=data, headers=auth_headers)


# Create car

def test_create_car_success(client, auth_headers):
    response = create_car(client, auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My BMW"
    assert data["make"] == "BMW"
    assert data["model"] == "M3"
    assert data["year"] == 2020
    assert "car_uuid" in data

def test_create_car_unauthorized(client):
    response = client.post("/cars/", json=CAR_PAYLOAD)
    assert response.status_code == 401


# Get cars

def test_get_cars_success(client, auth_headers):
    create_car(client, auth_headers)
    response = client.get("/cars/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_cars_empty(client, auth_headers):
    response = client.get("/cars/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_cars_unauthorized(client):
    response = client.get("/cars/")
    assert response.status_code == 401


# Get car

def test_get_car_by_uuid_success(client, auth_headers):
    created = create_car(client, auth_headers).json()
    response = client.get(f"/cars/{created['car_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["car_uuid"] == created["car_uuid"]

def test_get_car_not_found(client, auth_headers):
    response = client.get(f"/cars/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_get_car_wrong_user(client, auth_headers):
    created = create_car(client, auth_headers).json()
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.get(f"/cars/{created['car_uuid']}", headers=other_headers)
    assert response.status_code == 403


# Update car

def test_update_car_success(client, auth_headers):
    created = create_car(client, auth_headers).json()
    response = client.put(
        f"/cars/{created['car_uuid']}",
        json={"mileage": 60000, "name": "Updated BMW"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["mileage"] == 60000
    assert response.json()["name"] == "Updated BMW"

def test_update_car_not_found(client, auth_headers):
    response = client.put(
        f"/cars/{uuid4()}",
        json={"mileage": 60000},
        headers=auth_headers,
    )
    assert response.status_code == 404


# Delete car

def test_delete_car_success(client, auth_headers):
    created = create_car(client, auth_headers).json()
    response = client.delete(f"/cars/{created['car_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    get = client.get(f"/cars/{created['car_uuid']}", headers=auth_headers)
    assert get.status_code == 404

def test_delete_car_not_found(client, auth_headers):
    response = client.delete(f"/cars/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_car_wrong_user(client, auth_headers):
    created = create_car(client, auth_headers).json()
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.delete(f"/cars/{created['car_uuid']}", headers=other_headers)
    assert response.status_code == 403


# Get car report

def test_get_car_report_success(client, auth_headers):
    created = create_car(client, auth_headers).json()
    response = client.get(f"/cars/{created['car_uuid']}/report", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_get_car_report_not_found(client, auth_headers):
    response = client.get(f"/cars/{uuid4()}/report", headers=auth_headers)
    assert response.status_code == 404