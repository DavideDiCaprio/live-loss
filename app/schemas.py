from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from .models import UserType 
import re

# --- User Schemas ---

class UserBase(BaseModel):
    email: EmailStr
    nickname: str = Field(..., min_length=3, max_length=50) 
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=18) 

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain an uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain a lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain a number')
        return v
    

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
