from uuid import uuid4
from tests.conftest import register_user
from datetime import datetime, timezone, timedelta

PAST_TS = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp() * 1000)

CAR_PAYLOAD = {
    "name": "My BMW",
    "make": "BMW",
    "model": "M3",
    "year": 2020,
    "vin": "WBS8M9C50J5J12345",
    "mileage": 50000,
    "license_plate": "CJ01ABC",
}

TASK_PAYLOAD = {
    "title": "Oil Change",
    "category": "Engine",
    "mileage": 50000,
    "cost": 100.0,
    "completed_date": PAST_TS,
}

def create_car(client, auth_headers):
    payload = {**CAR_PAYLOAD, "car_uuid": str(uuid4())}
    return client.post("/cars/", json=payload, headers=auth_headers).json()

def create_task(client, auth_headers, car_uuid):
    payload = {**TASK_PAYLOAD, "car_uuid": str(car_uuid), "task_uuid": str(uuid4())}
    return client.post("/tasks/", json=payload, headers=auth_headers).json()

def create_invoice(client, auth_headers, task_uuid):
    return client.post("/invoices/", json={
            "task_uuid": str(task_uuid),
            "file_key": "invoices/test.pdf",
            "file_name": "test.pdf",
            "file_type": "application/pdf",
            "file_size": 1024,
        },
        headers=auth_headers,
    )


# Create 

def test_create_invoice_success(client, auth_headers):
    car = create_car(client, auth_headers)
    task = create_task(client, auth_headers, car["car_uuid"])
    response = create_invoice(client, auth_headers, task["task_uuid"])
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.pdf"
    assert data["file_type"] == "application/pdf"
    assert "invoice_uuid" in data

def test_create_invoice_task_not_found(client, auth_headers):
    response = create_invoice(client, auth_headers, uuid4())
    assert response.status_code == 404

def test_create_invoice_unauthorized(client):
    response = client.post("/invoices/",json={
            "task_uuid": str(uuid4()),
            "file_key": "invoices/test.pdf",
            "file_name": "test.pdf",
            "file_type": "application/pdf",
            "file_size": 1024,
    })
    assert response.status_code == 401


# Get task invoices

def test_get_task_invoices_empty(client, auth_headers):
    car = create_car(client, auth_headers)
    task = create_task(client, auth_headers, car["car_uuid"])
    response = client.get(f"/invoices/task/{task['task_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_task_invoices_success(client, auth_headers):
    car = create_car(client, auth_headers)
    task = create_task(client, auth_headers, car["car_uuid"])
    create_invoice(client, auth_headers, task["task_uuid"])
    create_invoice(client, auth_headers, task["task_uuid"])
    response = client.get(f"/invoices/task/{task['task_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_task_invoices_task_not_found(client, auth_headers):
    response = client.get(f"/invoices/task/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_get_task_invoices_wrong_user(client, auth_headers):
    car = create_car(client, auth_headers)
    task = create_task(client, auth_headers, car["car_uuid"])
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.get(f"/invoices/task/{task['task_uuid']}", headers=other_headers)
    assert response.status_code == 404


# Get download link

def test_get_download_link_success(client, auth_headers):
    car = create_car(client, auth_headers)
    task = create_task(client, auth_headers, car["car_uuid"])
    invoice = create_invoice(client, auth_headers, task["task_uuid"]).json()
    response = client.get(f"/invoices/{invoice['invoice_uuid']}/download", headers=auth_headers)
    assert response.status_code == 200
    assert "download_url" in response.json()
    assert response.json()["download_url"] == "https://mock-url.com/file"

def test_get_download_link_not_found(client, auth_headers):
    response = client.get(f"/invoices/{uuid4()}/download", headers=auth_headers)
    assert response.status_code == 404


# Delete invoice

def test_delete_invoice_success(client, auth_headers):
    car = create_car(client, auth_headers)
    task = create_task(client, auth_headers, car["car_uuid"])
    invoice = create_invoice(client, auth_headers, task["task_uuid"]).json()
    response = client.delete(f"/invoices/{invoice['invoice_uuid']}", headers=auth_headers)
    assert response.status_code == 200
    get = client.get(f"/invoices/task/{task['task_uuid']}", headers=auth_headers)
    assert get.json() == []

def test_delete_invoice_not_found(client, auth_headers):
    response = client.delete(f"/invoices/{uuid4()}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_invoice_wrong_user(client, auth_headers):
    car = create_car(client, auth_headers)
    task = create_task(client, auth_headers, car["car_uuid"])
    invoice = create_invoice(client, auth_headers, task["task_uuid"]).json()
    register_user(client, email="other@example.com")
    login = client.post("/auth/login", json={
        "email": "other@example.com",
        "password": "testpassword123",
    })
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.delete(f"/invoices/{invoice['invoice_uuid']}", headers=other_headers)
    assert response.status_code == 404