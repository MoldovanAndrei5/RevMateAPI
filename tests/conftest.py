import os
from unittest.mock import patch

# Set env vars
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "ci_db")
os.environ.setdefault("DB_USERNAME", "ci_user")
os.environ.setdefault("DB_PASSWORD", "ci_password")
os.environ.setdefault("JWT_SECRET", "test_secret_key_for_ci_testing_very_secure_key")
os.environ.setdefault("ALGORITHM", "HS256")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from database import engine, Base, SessionLocal
from app import create_app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()

@pytest.fixture(autouse=True)
def mock_s3():
    with (patch("services.invoice_service.generate_presigned_download_url", return_value="https://mock-url.com/file"), 
          patch("services.car_service.generate_presigned_download_url", return_value="https://mock-url.com/file"), 
          patch("services.invoice_service.delete_file", return_value=None),
          patch("services.car_service.delete_file", return_value=None), 
          patch("services.task_service.delete_file", return_value=None), 
          patch("services.account_service.delete_file", return_value=None)):
        yield

@pytest.fixture(autouse=True)
def mock_email():
    with patch("services.email_proxy_service.EmailProxyService.send_otp"):
        yield

@pytest.fixture(scope="session")
def client():
    app = create_app()
    return TestClient(app)

def get_otp(email: str) -> str:
    db = SessionLocal()
    try:
        result = db.execute(
            text(
                "SELECT otp_code FROM otp_codes "
                "WHERE email = :email "
                "ORDER BY expires_at DESC LIMIT 1"
            ),
            {"email": email},
        ).fetchone()
        return str(result[0])
    finally:
        db.close()

def register_user(
    client,
    email="test@example.com",
    password="testpassword123",
    first_name="Test",
    last_name="User",
):
    client.post("/auth/send-otp", json={"email": email})
    otp = get_otp(email)
    return client.post("/auth/register", json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "otp_code": otp,
    })

@pytest.fixture
def auth_headers(client):
    register_user(client)
    response = client.post("/auth/login",json={
            "email": "test@example.com",
            "password": "testpassword123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}