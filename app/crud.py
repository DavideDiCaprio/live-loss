from sqlalchemy.orm import Session
from .database import models
from .models import user as user_schema

def get_user(db: Session, user_id: int):
    """
    Retrieves a single user from the database by their ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_name(db: Session, name: str):
    """
    Retrieves a single user from the database by their name.
    """
    return db.query(models.User).filter(models.User.name == name).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of users from the database with optional pagination.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: user_schema.UserCreate):
    """
    Creates a new user in the database.
    """
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user