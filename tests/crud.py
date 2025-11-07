import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from app import crud, schemas, models
from app.models import UserType

fake = Faker()

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """
    Test creating a user and verifying its default values.
    """
    email = fake.unique.email()
    nickname = fake.unique.user_name()
    password = "password123"
    
    user_in = schemas.UserCreate(
        email=email,
        password=password,
        nickname=nickname
    )
    
    db_user = await crud.create_user(db_session, user=user_in)
    
    # Verify the user was created with correct data
    assert db_user.id is not None
    assert db_user.email == email
    assert db_user.nickname == nickname
    
    # Verify default values
    assert db_user.balance == 0.0
    assert db_user.user_type == UserType.NORMAL
    assert db_user.is_active == True
    assert db_user.hashed_password == f"hashed_{password}" # From our placeholder hasher

@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession):
    """
    Test getting a user by ID.
    """
    # First, create a user
    user_in = schemas.UserCreate(
        email=fake.unique.email(),
        password="pwd",
        nickname=fake.unique.user_name()
    )
    db_user = await crud.create_user(db_session, user=user_in)
    
    # Now, get the user
    retrieved_user = await crud.get_user(db_session, user_id=db_user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == db_user.id
    assert retrieved_user.email == db_user.email

@pytest.mark.asyncio
async def test_get_user_not_found(db_session: AsyncSession):
    """
    Test getting a non-existent user.
    """
    retrieved_user = await crud.get_user(db_session, user_id=999)
    assert retrieved_user is None

@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    """
    Test getting a user by email.
    """
    email = fake.unique.email()
    user_in = schemas.UserCreate(
        email=email,
        password="pwd",
        nickname=fake.unique.user_name()
    )
    await crud.create_user(db_session, user=user_in)
    
    retrieved_user = await crud.get_user_by_email(db_session, email=email)
    assert retrieved_user is not None
    assert retrieved_user.email == email

@pytest.mark.asyncio
async def test_get_users(db_session: AsyncSession):
    """
    Test getting a list of users.
    """
    # Create two users
    await crud.create_user(db_session, schemas.UserCreate(
        email=fake.unique.email(), password="p1", nickname=fake.unique.user_name()
    ))
    await crud.create_user(db_session, schemas.UserCreate(
        email=fake.unique.email(), password="p2", nickname=fake.unique.user_name()
    ))
    
    users = await crud.get_users(db_session, skip=0, limit=10)
    assert len(users) == 2
    
    # Test pagination (limit)
    users_limit = await crud.get_users(db_session, skip=0, limit=1)
    assert len(users_limit) == 1
    
    # Test pagination (skip)
    users_skip = await crud.get_users(db_session, skip=1, limit=10)
    assert len(users_skip) == 1
    assert users_skip[0].email != users[0].email

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """
    Test updating a user's details.
    """
    user_in = schemas.UserCreate(
        email=fake.unique.email(),
        password="pwd",
        nickname="original_nick"
    )
    db_user = await crud.create_user(db_session, user=user_in)
    
    update_data = schemas.UserUpdate(
        nickname="new_nick",
        balance=150.75,
        user_type=UserType.PREMIUM
    )
    
    updated_user = await crud.update_user(db_session, user_id=db_user.id, user_update=update_data)
    
    assert updated_user is not None
    assert updated_user.id == db_user.id
    assert updated_user.nickname == "new_nick"
    assert updated_user.balance == 150.75
    assert updated_user.user_type == UserType.PREMIUM
    assert updated_user.email == db_user.email 

@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    """
    Test deleting a user.
    """
    user_in = schemas.UserCreate(
        email=fake.unique.email(),
        password="pwd",
        nickname=fake.unique.user_name()
    )
    db_user = await crud.create_user(db_session, user=user_in)
    
    user_id = db_user.id
    
    deleted_user = await crud.delete_user(db_session, user_id=user_id)
    
    assert deleted_user is not None
    assert deleted_user.id == user_id
    
    retrieved_user = await crud.get_user(db_session, user_id=user_id)
    assert retrieved_user is None
