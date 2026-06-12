from tests.conftest import get_otp

def register_user(client, email="test@example.com", password="testpassword123", first_name="Test", last_name="User"):
    client.post("/auth/send-otp", json={"email": email})
    otp = get_otp(email)
    return client.post("/auth/register", json={
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "otp_code": otp,
    })


# Send otp

def test_send_register_otp_success(client):
    response = client.post("/auth/send-otp", json={"email": "new@example.com"})
    assert response.status_code == 200
    assert "message" in response.json()

def test_send_register_otp_already_registered(client):
    register_user(client)
    response = client.post("/auth/send-otp", json={"email": "test@example.com"})
    assert response.status_code == 400


# Register

def test_register_success(client):
    client.post("/auth/send-otp", json={"email": "new@example.com"})
    otp = get_otp("new@example.com")
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "testpassword123",
        "first_name": "New",
        "last_name": "User",
        "otp_code": otp,
    })
    assert response.status_code == 200
    assert "message" in response.json()

def test_register_wrong_otp(client):
    client.post("/auth/send-otp", json={"email": "new@example.com"})
    response = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "testpassword123",
        "first_name": "New",
        "last_name": "User",
        "otp_code": "000000",
    })
    assert response.status_code == 401

def test_register_no_otp_sent(client):
    response = client.post("/auth/register", json={
        "email": "nootp@example.com",
        "password": "testpassword123",
        "first_name": "No",
        "last_name": "Otp",
        "otp_code": "123456",
    })
    assert response.status_code == 404


# Login

def test_login_success(client):
    register_user(client)
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user_id" in data

def test_login_wrong_password(client):
    register_user(client)
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401

def test_login_wrong_email(client):
    response = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "testpassword123",
    })
    assert response.status_code == 401


# Forgot password

def test_forgot_password_send_otp_success(client):
    register_user(client)
    response = client.post("/auth/forgot-password/send-otp", json={"email": "test@example.com"})
    assert response.status_code == 200

def test_forgot_password_send_otp_unknown_email(client):
    response = client.post("/auth/forgot-password/send-otp", json={"email": "nobody@example.com"})
    assert response.status_code == 404

def test_forgot_password_reset_success(client):
    register_user(client)
    client.post("/auth/forgot-password/send-otp", json={"email": "test@example.com"})
    otp = get_otp("test@example.com")
    response = client.post("/auth/forgot-password/reset", json={
        "email": "test@example.com",
        "otp_code": otp,
        "new_password": "newpassword123",
    })
    assert response.status_code == 200
    login = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "newpassword123",
    })
    assert login.status_code == 200

def test_forgot_password_reset_wrong_otp(client):
    register_user(client)
    client.post("/auth/forgot-password/send-otp", json={"email": "test@example.com"})
    response = client.post("/auth/forgot-password/reset", json={
        "email": "test@example.com",
        "otp_code": "000000",
        "new_password": "newpassword123",
    })
    assert response.status_code == 401