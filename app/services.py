from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import crud, models 

async def get_sorted_leaderboard_users(db: AsyncSession, limit: int = 10) -> List[models.User]:
    """Fetches users and sorts them by balance for the leaderboard.

    Args:
        db (AsyncSession): The database session.
        limit (int, optional): The maximum number of users to fetch
            before sorting. Defaults to 10.

    Returns:
        List[models.User]: A list of user models, sorted by
            their balance in descending order.
    """

    users = await crud.get_users(db, skip=0, limit=limit)
    
    sorted_users = sorted(users, key=lambda user: user.balance, reverse=True)
    
    return sorted_users
