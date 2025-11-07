from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List, Optional
from . import models, schemas
from .security import get_password_hash

'''
def get_password_hash(password: str):
    return f"hashed_{password}" 
'''

# --- CREATE ---
async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    """
    Creates a new user in the database.
    """
    hashed_password = get_password_hash(user.password)
    
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        nickname=user.nickname,
        balance=0.0,
        user_type=models.UserType.NORMAL 
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- READ ---
async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """
    Get a single user by their ID.
    """
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """
    Get a single user by their email.
    """
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def get_user_by_nickname(db: AsyncSession, nickname: str) -> Optional[models.User]:
    """
    Get a single user by their nickname.
    """
    result = await db.execute(select(models.User).filter(models.User.nickname == nickname))
    return result.scalars().first()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get a list of users with pagination.
    """
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

# --- UPDATE ---
async def update_user(db: AsyncSession, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """
    Update a user's details.
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- DELETE ---
async def delete_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """
    Delete a user by their ID.
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
        
    await db.delete(db_user)
    await db.commit()
    return db_user