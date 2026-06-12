from sqlalchemy import text
from database import SessionLocal
from uuid import uuid4
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

PAST_TS = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp() * 1000)
FUTURE_TS = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp() * 1000)

def create_car(client, auth_headers):
    payload = {**CAR_PAYLOAD, "car_uuid": str(uuid4())}
    return client.post("/cars/", json=payload, headers=auth_headers).json()

def create_task(client, auth_headers, car_uuid, **overrides):
    payload = {
        "task_uuid": str(uuid4()),
        "car_uuid": str(car_uuid),
        "title": "Oil Change",
        "category": "Engine",
        "cost": "150.00",
        "completed_date": PAST_TS,
        **overrides,
    }
    return client.post("/tasks/", json=payload, headers=auth_headers).json()


# Reset password

def test_reset_password_success(client, auth_headers):
    response = client.put(
        "/account/reset-password",
        json={"password": "newpassword123"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "message" in response.json()
    login = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "newpassword123",
    })
    assert login.status_code == 200

def test_reset_password_unauthorized(client):
    response = client.put(
        "/account/reset-password",
        json={"password": "newpassword123"},
    )
    assert response.status_code == 401


# Get stats

def test_get_stats_with_data(client, auth_headers):
    car = create_car(client, auth_headers)
    create_task(client, auth_headers, car["car_uuid"], category="Engine", cost="150.00", completed_date=PAST_TS)
    create_task(client, auth_headers, car["car_uuid"], title="Tire Rotation", category="Tires", cost="50.00", completed_date=None, scheduled_date=FUTURE_TS)
    create_task(client, auth_headers, car["car_uuid"], title="Brake Check", category="Brakes", cost="100.00", completed_date=None, scheduled_date=PAST_TS)
    response = client.get("/account/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 3
    assert data["completed_tasks"] == 1
    assert data["pending_tasks"] == 1
    assert data["overdue_tasks"] == 1
    assert data["total_spent"] == 300.0
    assert data["spent_by_category"]["Engine"] == 150.0
    assert data["spent_by_category"]["Tires"] == 50.0
    assert data["spent_by_category"]["Brakes"] == 100.0
    assert len(data["tasks_by_month"]) >= 1

def test_get_stats_empty(client, auth_headers):
    response = client.get("/account/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 0
    assert data["total_spent"] == 0.0
    assert data["completed_tasks"] == 0
    assert data["pending_tasks"] == 0
    assert data["overdue_tasks"] == 0

def test_get_stats_unauthorized(client):
    response = client.get("/account/stats")
    assert response.status_code == 401


# Send delete otp

def test_send_delete_otp_success(client, auth_headers):
    response = client.post(
        "/account/send-delete-otp",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "message" in response.json()

def test_send_delete_otp_unauthorized(client):
    response = client.post("/account/send-delete-otp")
    assert response.status_code == 401


# Delete account

def test_delete_account_success(client, auth_headers):
    client.post("/account/send-delete-otp", headers=auth_headers)
    # Read otp from db
    db = SessionLocal()
    try:
        result = db.execute(
            text(
                "SELECT otp_code FROM otp_codes "
                "WHERE email = :email "
                "ORDER BY expires_at DESC LIMIT 1"
            ),
            {"email": "test@example.com"},
        ).fetchone()
        otp = str(result[0])
    finally:
        db.close()
    response = client.request(
        "DELETE",
        "/account/delete-account",
        json={"otp_code": otp},
        headers=auth_headers,
    )
    assert response.status_code == 200
    login = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123",
    })
    assert login.status_code == 401

def test_delete_account_wrong_otp(client, auth_headers):
    client.post("/account/send-delete-otp", headers=auth_headers)
    response = client.request(
        "DELETE",
        "/account/delete-account",
        json={"otp_code": "000000"},
        headers=auth_headers,
    )
    assert response.status_code == 401

def test_delete_account_no_otp_sent(client, auth_headers):
    response = client.request(
        "DELETE",
        "/account/delete-account",
        json={"otp_code": "123456"},
        headers=auth_headers,
    )
    assert response.status_code == 404