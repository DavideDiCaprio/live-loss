from pydantic import BaseModel, Field
from typing import List

class Figure(BaseModel):
    """
    Represents a single figure in the 'Get Bonus' game.
    """
    name: str = Field(..., description="The name of the figure (e.g., 'Cherry', 'Diamond').")
    bonus: int = Field(..., description="The bonus value associated with the figure.", ge=0)

class GameResult(BaseModel):
    """
    Represents the result of a single 'Get Bonus' game round.
    """
    figures: List[Figure]
    total_bonus: int
    new_credit: int
