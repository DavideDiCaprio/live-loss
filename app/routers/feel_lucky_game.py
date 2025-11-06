from fastapi import APIRouter, Depends
from pydantic import BaseModel
import random
from sqlalchemy.ext.asyncio import AsyncSession  

from ..database import get_db 
from .. import crud, schemas   

BONUS_AMOUNT: float = 100.0

router = APIRouter(
    prefix="/api/games",
    tags=["Games"]
)

# Define Pydantic models for this game
class GamePlay(BaseModel):
    choice: int  
    user_id: int

class GameResult(BaseModel):
    result: str  # "win" or "lose"
    bonusIndex: int  

@router.post("/feel-lucky", response_model=GameResult)
async def play_feel_lucky_game(play: GamePlay, db: AsyncSession = Depends(get_db)):
    """
    Handles the "Feel Lucky" game logic securely on the server.
    """
    emojis_count = 6  # 6 emojis
    
    server_bonus_index = random.randint(0, emojis_count - 1)
    
    if play.choice == server_bonus_index:
        result = "win"
        
        try:
            user = await crud.get_user(db, user_id=play.user_id)
            if user:
                new_balance = user.balance + BONUS_AMOUNT
                update_data = schemas.UserUpdate(balance=new_balance)
                await crud.update_user(db, user_id=play.user_id, user_update=update_data)
                print(f"User {user.nickname} won! New balance: {new_balance}")
            else:
                # This case should ideally not happen if the frontend sends a valid ID
                print(f"Error: User {play.user_id} not found, cannot update balance.")
        except Exception as e:
            print(f"Error updating balance for user {play.user_id}: {e}")
            # Don't let a DB error stop the game result from being sent
        # --- End of added logic ---

    else:
        result = "lose"

    # Return the result and the correct answer
    return GameResult(result=result, bonusIndex=server_bonus_index)