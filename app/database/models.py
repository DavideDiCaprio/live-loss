from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    """
    'users' table in the database
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    credit = Column(Integer, default=0)
    gambling_losses = Column(Integer, default=0)
