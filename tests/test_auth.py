import pytest

from conftest import register_user


def test_registration_creates_user_and_logs_them_in(client):
    response = register_user(client)

    assert response.status_code == 200
    assert response.json == {"success": True, "redirect": "/stages"}
    stages = client.get("/api/stages")
    assert stages.status_code == 200
    assert stages.json[0]["unlocked"] is True


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "test@example.com", "password": "valid-password"},
        {"username": "test-user", "password": "valid-password"},
        {"username": "test-user", "email": "test@example.com"},
    ],
)
def test_registration_requires_all_fields(client, payload):
    response = client.post("/api/register", json=payload)

    assert response.status_code == 400
    assert response.json["error"] == "All fields are required"


def test_registration_rejects_short_username(client):
    response = register_user(client, username="ab")

    assert response.status_code == 400
    assert response.json["error"] == "Username must be at least 3 characters"


def test_registration_rejects_short_password(client):
    response = register_user(client, password="short")

    assert response.status_code == 400
    assert response.json["error"] == "Password must be at least 8 characters"


@pytest.mark.parametrize(
    ("username", "email"),
    [
        ("test-user", "another@example.com"),
        ("another-user", "test@example.com"),
    ],
)
def test_registration_rejects_duplicate_username_or_email(client, username, email):
    register_user(client)

    response = register_user(client, username=username, email=email)

    assert response.status_code == 409
    assert response.json["error"] == "Username or email already exists"


@pytest.mark.parametrize("login_name", ["test-user", "TEST@example.com"])
def test_login_accepts_username_or_email(client, login_name):
    register_user(client)
    client.post("/api/logout")

    response = client.post(
        "/api/login",
        json={"username": login_name, "password": "valid-password"},
    )

    assert response.status_code == 200
    assert response.json == {"success": True, "redirect": "/stages"}
    assert client.get("/api/stages").status_code == 200


def test_login_rejects_incorrect_password(client):
    register_user(client)
    client.post("/api/logout")

    response = client.post(
        "/api/login",
        json={"username": "test-user", "password": "incorrect-password"},
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid username or password"


def test_login_requires_username_and_password(client):
    response = client.post("/api/login", json={"username": "test-user"})

    assert response.status_code == 400
    assert response.json["error"] == "All fields are required"
