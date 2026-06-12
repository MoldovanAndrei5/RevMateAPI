from uuid import uuid4
from tests.conftest import register_user

CAR_PAYLOAD = {
    "name": "My BMW",
    "make": "BMW",
    "model": "M3",
    "year": 2020,
    "vin": "WBS8M9C50J5J12345",
    "mileage": 50000,
    "license_plate": "CJ01ABC",
}

def create_car(client, auth_headers):
    payload = {**CAR_PAYLOAD, "car_uuid": str(uuid4())}
    return client.post("/cars/", json=payload, headers=auth_headers).json()

def create_two_users(client):
    register_user(client, email="sender@example.com")
    login1 = client.post("/auth/login", json={
        "email": "sender@example.com",
        "password": "testpassword123",
    })
    sender_headers = {"Authorization": f"Bearer {login1.json()['access_token']}"}
    register_user(client, email="receiver@example.com")
    login2 = client.post("/auth/login", json={
        "email": "receiver@example.com",
        "password": "testpassword123",
    })
    receiver_headers = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    return sender_headers, receiver_headers

def initiate_transfer(client, sender_headers, car_uuid, receiver_email="receiver@example.com"):
    return client.post("/transfers/initiate",json={
            "car_uuid": str(car_uuid),
            "receiver_email": receiver_email,
        },
        headers=sender_headers,
    )


# Initiate transfer

def test_initiate_transfer_success(client):
    sender_headers, _ = create_two_users(client)
    car = create_car(client, sender_headers)
    response = initiate_transfer(client, sender_headers, car["car_uuid"])
    assert response.status_code == 200
    data = response.json()
    assert data["car_uuid"] == car["car_uuid"]
    assert data["receiver_email"] == "receiver@example.com"
    assert data["status"] == "pending"
    assert "transfer_uuid" in data

def test_initiate_transfer_car_not_found(client):
    sender_headers, _ = create_two_users(client)
    response = initiate_transfer(client, sender_headers, uuid4())
    assert response.status_code == 404

def test_initiate_transfer_receiver_not_found(client):
    sender_headers, _ = create_two_users(client)
    car = create_car(client, sender_headers)
    response = initiate_transfer(
        client, sender_headers, car["car_uuid"],
        receiver_email="nobody@example.com"
    )
    assert response.status_code == 404

def test_initiate_transfer_to_self(client):
    sender_headers, _ = create_two_users(client)
    car = create_car(client, sender_headers)
    response = initiate_transfer(
        client, sender_headers, car["car_uuid"],
        receiver_email="sender@example.com"
    )
    assert response.status_code == 400

def test_initiate_transfer_wrong_car_owner(client):
    sender_headers, receiver_headers = create_two_users(client)
    car = create_car(client, sender_headers)
    response = initiate_transfer(client, receiver_headers, car["car_uuid"])
    assert response.status_code == 403

def test_initiate_transfer_duplicate(client):
    sender_headers, _ = create_two_users(client)
    car = create_car(client, sender_headers)
    initiate_transfer(client, sender_headers, car["car_uuid"])
    response = initiate_transfer(client, sender_headers, car["car_uuid"])
    assert response.status_code == 400


# Get incoming / outgoing

def test_get_outgoing_success(client):
    sender_headers, _ = create_two_users(client)
    car = create_car(client, sender_headers)
    initiate_transfer(client, sender_headers, car["car_uuid"])
    response = client.get("/transfers/outgoing", headers=sender_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_incoming_success(client):
    sender_headers, receiver_headers = create_two_users(client)
    car = create_car(client, sender_headers)
    initiate_transfer(client, sender_headers, car["car_uuid"])
    response = client.get("/transfers/incoming", headers=receiver_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_incoming_empty(client):
    sender_headers, _ = create_two_users(client)
    response = client.get("/transfers/incoming", headers=sender_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_outgoing_empty(client):
    sender_headers, _ = create_two_users(client)
    response = client.get("/transfers/outgoing", headers=sender_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_transfers_unauthorized(client):
    assert client.get("/transfers/incoming").status_code == 401
    assert client.get("/transfers/outgoing").status_code == 401


# Accept transfer

def test_accept_transfer_success(client):
    sender_headers, receiver_headers = create_two_users(client)
    car = create_car(client, sender_headers)
    transfer = initiate_transfer(client, sender_headers, car["car_uuid"]).json()
    response = client.post(f"/transfers/accept/{transfer['transfer_uuid']}", headers=receiver_headers)
    assert response.status_code == 200
    cars = client.get("/cars/", headers=receiver_headers).json()
    assert any(c["car_uuid"] == car["car_uuid"] for c in cars)

def test_accept_transfer_wrong_user(client):
    sender_headers, receiver_headers = create_two_users(client)
    car = create_car(client, sender_headers)
    transfer = initiate_transfer(client, sender_headers, car["car_uuid"]).json()
    response = client.post(f"/transfers/accept/{transfer['transfer_uuid']}", headers=sender_headers)
    assert response.status_code == 403

def test_accept_transfer_not_found(client):
    sender_headers, _ = create_two_users(client)
    response = client.post(f"/transfers/accept/{uuid4()}", headers=sender_headers)
    assert response.status_code == 404


# Reject transfer

def test_reject_transfer_success(client):
    sender_headers, receiver_headers = create_two_users(client)
    car = create_car(client, sender_headers)
    transfer = initiate_transfer(client, sender_headers, car["car_uuid"]).json()
    response = client.post(f"/transfers/reject/{transfer['transfer_uuid']}", headers=receiver_headers)
    assert response.status_code == 200
    incoming = client.get("/transfers/incoming", headers=receiver_headers).json()
    assert incoming == []

def test_reject_transfer_wrong_user(client):
    sender_headers, receiver_headers = create_two_users(client)
    car = create_car(client, sender_headers)
    transfer = initiate_transfer(client, sender_headers, car["car_uuid"]).json()
    response = client.post(f"/transfers/reject/{transfer['transfer_uuid']}", headers=sender_headers)
    assert response.status_code == 403


# Cancel transfer

def test_cancel_transfer_success(client):
    sender_headers, _ = create_two_users(client)
    car = create_car(client, sender_headers)
    transfer = initiate_transfer(client, sender_headers, car["car_uuid"]).json()
    response = client.request(
        "DELETE",
        f"/transfers/cancel/{transfer['transfer_uuid']}",
        headers=sender_headers,
    )
    assert response.status_code == 200
    outgoing = client.get("/transfers/outgoing", headers=sender_headers).json()
    assert outgoing == []

def test_cancel_transfer_wrong_user(client):
    sender_headers, receiver_headers = create_two_users(client)
    car = create_car(client, sender_headers)
    transfer = initiate_transfer(client, sender_headers, car["car_uuid"]).json()
    response = client.request(
        "DELETE",
        f"/transfers/cancel/{transfer['transfer_uuid']}",
        headers=receiver_headers,
    )
    assert response.status_code == 403

def test_cancel_transfer_not_found(client):
    sender_headers, _ = create_two_users(client)
    response = client.request(
        "DELETE",
        f"/transfers/cancel/{uuid4()}",
        headers=sender_headers,
    )
    assert response.status_code == 404