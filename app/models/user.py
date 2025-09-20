from pydantic import BaseModel, Field

class User(BaseModel):
    """
    Represents a user in the application.
    """
    name: str = Field(..., description="The user's name.")
    credit: int = Field(..., description="The amount of credit the user has.", ge=0)
    gambling_losses: int = Field(..., description="The total amount the user has lost.", ge=0)
