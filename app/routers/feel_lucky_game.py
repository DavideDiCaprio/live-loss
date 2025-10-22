from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(
    prefix="/api/games",
    tags=["Games"]
)

# Define Pydantic models for this game
class GamePlay(BaseModel):
    choice: int  

class GameResult(BaseModel):
    result: str  # "win" or "lose"
    bonusIndex: int  # The correct index

@router.post("/feel-lucky", response_model=GameResult)
async def play_feel_lucky_game(play: GamePlay):
    """
    Handles the "Feel Lucky" game logic securely on the server.
    """
    emojis_count = 6  # 6 emojis
    
    # Securely pick the winning index
    server_bonus_index = random.randint(0, emojis_count - 1)

    # Check if the user's choice matched the server's
    if play.choice == server_bonus_index:
        result = "win"
    else:
        result = "lose"

    # Return the result and the correct answer
    return GameResult(result=result, bonusIndex=server_bonus_index)