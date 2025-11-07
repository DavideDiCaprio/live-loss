"""
SQLAlchemy ORM models defining the database structure for the User entity.
"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, Final

from .database import Base 

# --- Enumerations ---

class UserType(str, enum.Enum):
    """
    Defines the available roles or types a user can have within the application.

    This enumeration is stored in the database as a string type.
    """
    ADMIN = 'Admin'
    NORMAL = "Normal"
    PROFESSIONAL_GAMBLER = "Professional Gambler"

# --- ORM Models ---

class User(Base):
    """
    Represents the User table in the database.

    Attributes define the columns, types, constraints, and default values
    for the user entity.
    """
    __tablename__: Final[str] = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    """The unique, auto-incrementing primary key ID for the user."""
    
    # --- Required/Unique Fields ---
    
    nickname: Mapped[str] = mapped_column(String, unique=True, index=True)
    """The user's unique nickname, indexed for fast lookups."""
    
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    """The user's unique email address, indexed for fast lookups."""
    
    hashed_password: Mapped[str] = mapped_column(String)
    """The securely hashed password string."""
    
    # --- Status/System Fields ---
    
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    """The user's current floating-point balance, defaulting to 0.0."""
    
    user_type: Mapped[UserType] = mapped_column(
        Enum(UserType),
        default=UserType.NORMAL
    )
    """
    The user's role or type, defined by the UserType enumeration.
    Defaults to UserType.NORMAL.
    """
    
    is_active: Mapped[bool] = mapped_column(default=True)
    """The user's active status, defaulting to True."""