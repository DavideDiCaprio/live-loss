from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .models import UserType 

# --- User Schemas ---

class UserBase(BaseModel):
    email: EmailStr
    nickname: str = Field(..., min_length=3, max_length=50) 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18) 

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18)
    balance: Optional[float] = Field(None, ge=0) 
    user_type: Optional[UserType] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    balance: float
    user_type: UserType
    
    class Config:
        from_attributes = True
