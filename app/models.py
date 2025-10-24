import enum
from sqlalchemy import Column, Integer, String, Boolean, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .database import Base 

# Define an Enum for UserType
class UserType(str, enum.Enum):
    NORMAL = "Normal"
    PREMIUM = "Premium"
    PROFESSIONAL_GAMBLER = "Professional Gambler"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    first_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    nickname: Mapped[str] = mapped_column(String, unique=True, index=True)
    
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    
    user_type: Mapped[UserType] = mapped_column(Enum(UserType), default=UserType.NORMAL)

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
