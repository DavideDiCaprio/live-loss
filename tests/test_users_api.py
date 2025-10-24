import pytest
import pytest_asyncio
from httpx import AsyncClient
from faker import Faker

fake = Faker()

@pytest.mark.asyncio
async def test_api_create_user(async_client: AsyncClient):
    """
    Test the POST /users/ endpoint.
    """
    email = fake.unique.email()
    nickname = fake.unique.user_name()
    password = "api_password123"
    
    user_data = {
        "email": email,
        "nickname": nickname,
        "password": password,
        "first_name": "API",
        "last_name": "Test"
    }
    
    response = await async_client.post("/users/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == email
    assert data["nickname"] == nickname
    assert data["first_name"] == "API"
    assert "id" in data
    assert "password" not in data # Ensure password isn't returned
    assert data["balance"] == 0.0 # Check default

@pytest.mark.asyncio
async def test_api_create_user_conflict(async_client: AsyncClient):
    """
    Test creating a user that conflicts with an existing one.
    """
    email = fake.unique.email()
    nickname = fake.unique.user_name()
    
    # Create the first user
    user_data_1 = {
        "email": email,
        "nickname": nickname,
        "password": "pwd1"
    }
    response1 = await async_client.post("/users/", json=user_data_1)
    assert response1.status_code == 201
    
    # Attempt to create a user with the same email
    user_data_2 = {
        "email": email,
        "nickname": fake.unique.user_name(),
        "password": "pwd2"
    }
    response2 = await async_client.post("/users/", json=user_data_2)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"
    
    # Attempt to create a user with the same nickname
    user_data_3 = {
        "email": fake.unique.email(),
        "nickname": nickname,
        "password": "pwd3"
    }
    response3 = await async_client.post("/users/", json=user_data_3)
    assert response3.status_code == 400
    assert response3.json()["detail"] == "Nickname already taken"

@pytest.mark.asyncio
async def test_api_read_user(async_client: AsyncClient):
    """
    Test GET /users/{id}
    """
    # Create a user first
    user_data = {
        "email": fake.unique.email(),
        "nickname": fake.unique.user_name(),
        "password": "pwd"
    }
    create_response = await async_client.post("/users/", json=user_data)
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Now read the user
    read_response = await async_client.get(f"/users/{user_id}")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_api_read_user_not_found(async_client: AsyncClient):
    """
    Test GET /users/{id} for a non-existent user.
    """
    response = await async_client.get("/users/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_api_read_users(async_client: AsyncClient):
    """
    Test GET /users/
    """
    # Create two users
    await async_client.post("/users/", json={
        "email": fake.unique.email(),
        "nickname": fake.unique.user_name(),
        "password": "pwd1"
    })
    await async_client.post("/users/", json={
        "email": fake.unique.email(),
        "nickname": fake.unique.user_name(),
        "password": "pwd2"
    })
    
    # Read the list of users
    response = await async_client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

@pytest.mark.asyncio
async def test_api_update_user(async_client: AsyncClient):
    """
    Test PATCH /users/{id}
    """
    # Create a user
    user_data = {
        "email": fake.unique.email(),
        "nickname": "patch_me",
        "password": "pwd"
    }
    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Update the user's nickname and balance
    update_data = {
        "nickname": "i_am_patched",
        "balance": 100.0
    }
    update_response = await async_client.patch(f"/users/{user_id}", json=update_data)
    
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == user_id
    assert data["nickname"] == "i_am_patched"
    assert data["balance"] == 100.0
    assert data["email"] == user_data["email"] 

@pytest.mark.asyncio
async def test_api_delete_user(async_client: AsyncClient):
    """
    Test DELETE /users/{id}
    """
    # Create a user
    user_data = {
        "email": fake.unique.email(),
        "nickname": "delete_me",
        "password": "pwd"
    }
    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Delete the user
    delete_response = await async_client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == user_id
    
    # Verify the user is gone
    get_response = await async_client.get(f"/users/{user_id}")
    assert get_response.status_code == 404
