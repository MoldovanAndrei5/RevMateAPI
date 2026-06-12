from uuid import uuid4
from tests.conftest import register_user
from datetime import datetime, timezone, timedelta

CAR_PAYLOAD = {
    "name": "My BMW",
    "make": "BMW",
    "model": "M3",
    "year": 2020,
    "vin": "WBS8M9C50J5J12345",
    "mileage": 50000,
    "license_plate": "CJ01ABC",
}

FUTURE_TS = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp() * 1000)
PAST_TS = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp() * 1000)

SCHEDULED_TASK = {
    "title": "Oil Change",
    "category": "Engine",
    "mileage": 50000,
    "cost": "100.00",
    "scheduled_date": FUTURE_TS,
}

COMPLETED_TASK = {
    "title": "Brake Check",
    "category": "Brakes",
    "mileage": 48000,
    "cost": "200.00",
    "completed_date": PAST_TS,
}

def create_car(client, auth_headers):
    payload = {**CAR_PAYLOAD, "car_uuid": str(uuid4())}
    return client.post("/cars/", json=payload, headers=auth_headers).json()

def create_task(client, auth_headers, car_uuid, payload=None):
    data = {
        **(payload or SCHEDULED_TASK),
        "task_uuid": str(uuid4()),
        "car_uuid": str(car_uuid),
    }
    return client.post("/tasks/", json=data, headers=auth_headers)


# Create task

def test_create_scheduled_task_success(client, auth_headers):
    car = create_car(client, auth_headers)
    response = create_task(client, auth_headers, car["car_uuid"])
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Oil Change"
    assert data["category"] == "Engine"
    assert data["scheduled_date"] == FUTURE_TS
    assert data["completed_date"] is None
    assert "task_uuid" in data

def test_create_completed_task_success(client, auth_headers):
    car = create_car(client, auth_headers)
    response = create_task(client, auth_headers, car["car_uuid"], COMPLETED_TASK)
    assert response.status_code == 200
    data = response.json()
    assert data["completed_date"] == PAST_TS
    assert data["scheduled_date"] is None

def test_create_task_car_not_found(client, auth_headers):
    response = create_task(client, auth_headers, uuid4())
    assert response.status_code == 404

def test_create_task_wrong_car_owner(client, auth_headers):
    car = create_car(client, auth_headers)
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = create_task(client, other_headers, car["car_uuid"])
    assert response.status_code == 403

def test_create_task_unauthorized(client):
    response = client.post("/tasks/", json={
        **SCHEDULED_TASK,
        "task_uuid": str(uuid4()),
        "car_uuid": str(uuid4()),
    })
    assert response.status_code == 401


#  Get tasks

def test_get_tasks_success(client, auth_headers):
    car = create_car(client, auth_headers)
    create_task(client, auth_headers, car["car_uuid"])
    create_task(client, auth_headers, car["car_uuid"])
    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_tasks_empty(client, auth_headers):
    response = client.get("/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_unauthorized(client):
    response = client.get("/tasks/")
    assert response.status_code == 401


# Get task

def test_get_task_by_uuid_success(client, auth_headers):
    car = create_car(client, auth_headers)
    created = create_task(client, auth_headers, car["car_uuid"]).json()
    response = client.get(f"/tasks/{created['task_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["task_uuid"] == created["task_uuid"]

def test_get_task_not_found(client, auth_headers):
    response = client.get(f"/tasks/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_get_task_wrong_user(client, auth_headers):
    car = create_car(client, auth_headers)
    created = create_task(client, auth_headers, car["car_uuid"]).json()
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.get(f"/tasks/{created['task_uuid']}", headers=other_headers)
    assert response.status_code == 404


# Get car tasks

def test_get_car_tasks_success(client, auth_headers):
    car = create_car(client, auth_headers)
    create_task(client, auth_headers, car["car_uuid"])
    create_task(client, auth_headers, car["car_uuid"])
    response = client.get(f"/tasks/car/{car['car_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_car_tasks_car_not_found(client, auth_headers):
    response = client.get(f"/tasks/car/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_get_car_tasks_wrong_user(client, auth_headers):
    car = create_car(client, auth_headers)
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.get(f"/tasks/car/{car['car_uuid']}", headers=other_headers)
    assert response.status_code == 403


# Update task

def test_update_task_success(client, auth_headers):
    car = create_car(client, auth_headers)
    created = create_task(client, auth_headers, car["car_uuid"]).json()
    response = client.put(
        f"/tasks/{created['task_uuid']}",
        json={"title": "Updated Oil Change", "mileage": 55000},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Oil Change"
    assert response.json()["mileage"] == 55000

def test_update_task_not_found(client, auth_headers):
    response = client.put(
        f"/tasks/{uuid4()}",
        json={"title": "Updated"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    

# Delete task

def test_delete_task_success(client, auth_headers):
    car = create_car(client, auth_headers)
    created = create_task(client, auth_headers, car["car_uuid"]).json()
    response = client.delete(f"/tasks/{created['task_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    get = client.get(f"/tasks/{created['task_uuid']}", headers=auth_headers)
    assert get.status_code == 404

def test_delete_task_not_found(client, auth_headers):
    response = client.delete(f"/tasks/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_task_wrong_user(client, auth_headers):
    car = create_car(client, auth_headers)
    created = create_task(client, auth_headers, car["car_uuid"]).json()
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.delete(f"/tasks/{created['task_uuid']}", headers=other_headers)
    assert response.status_code == 404