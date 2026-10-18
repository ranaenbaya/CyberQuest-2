import os

import pytest

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://cyberquest:cyberquest-dev-password@localhost:55432/cyberquest_test",
)

from app import app, get_db  # noqa: E402


@pytest.fixture
def client():
    app.config.update(TESTING=True, SESSION_COOKIE_SECURE=False)
    return app.test_client()


@pytest.fixture(autouse=True)
def clear_database():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
        db.commit()
    finally:
        db.close()


def register_user(client, username="test-user", email="test@example.com", password="valid-password"):
    return client.post(
        "/api/register",
        json={"username": username, "email": email, "password": password},
    )
