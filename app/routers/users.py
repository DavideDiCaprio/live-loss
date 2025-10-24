from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: schemas.UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    """
    # Check if email or nickname already exists
    db_user_email = await crud.get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    db_user_nickname = await crud.get_user_by_nickname(db, nickname=user.nickname)
    if db_user_nickname:
        raise HTTPException(status_code=400, detail="Nickname already taken")
        
    return await crud.create_user(db=db, user=user)


@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of users.
    """
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a single user by ID.
    """
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}", response_model=schemas.User)
async def update_existing_user(
    user_id: int, 
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's details. 
    Only fields provided in the request body will be updated.
    """
    db_user = await crud.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check for nickname/email conflicts if they are being changed
    if user_update.email:
        db_user_email = await crud.get_user_by_email(db, email=user_update.email)
        if db_user_email and db_user_email.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")
            
    if user_update.nickname:
        db_user_nickname = await crud.get_user_by_nickname(db, nickname=user_update.nickname)
        if db_user_nickname and db_user_nickname.id != user_id:
            raise HTTPException(status_code=400, detail="Nickname already taken")

    # Re-fetch the user to apply updates (crud.update_user)
    updated_user = await crud.get_user(db, user_id=user_id)
    return updated_user


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_existing_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user by ID.
    """
    db_user = await crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
