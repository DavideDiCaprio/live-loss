# tests/test_users.py

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_user(client: TestClient, db_session: Session):
    """
    Test creating a new user.
    """
    response = client.post("/users/", json={"name": "Test User"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test User"
    assert "id" in data

def test_read_user(client: TestClient, db_session: Session):
    """
    Test reading a single user by ID.
    """
    response = client.post("/users/", json={"name": "Another User"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Another User"
    assert data["id"] == user_id

def test_read_users(client: TestClient, db_session: Session):
    """
    Test reading a list of users.
    """
    client.post("/users/", json={"name": "User One"})
    client.post("/users/", json={"name": "User Two"})

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2