from pydantic import BaseModel, Field

class UserBase(BaseModel):
    """
    Base model for a user, containing common attributes.
    """
    name: str = Field(..., description="The user's name.")

class UserCreate(UserBase):
    """
    Model for creating a new user.
    """
    pass

class User(UserBase):
    """
    Model for representing a user, including their ID, credit, and gambling losses.
    """
    id: int
    credit: int = Field(..., description="The amount of credit the user has.", ge=0)
    gambling_losses: int = Field(..., description="The total amount the user has lost.", ge=0)

    class Config:
        orm_mode = True