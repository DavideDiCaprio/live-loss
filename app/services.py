from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import crud, models 

async def get_sorted_leaderboard_users(db: AsyncSession) -> List[models.User]:
    """
    Fetches all users and sorts them by balance for the leaderboard display.
    """
    users = await crud.get_users(db, skip=0, limit=1000)
    sorted_users = sorted(users, key=lambda user: user.balance, reverse=True)
    
    return sorted_users