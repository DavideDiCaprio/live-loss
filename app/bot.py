import asyncio
import random
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app import crud, schemas, models
from app.models import UserType
from app.websockets import ConnectionManager
from app.routers.feel_lucky_game import BONUS_AMOUNT

async def play_game_as_bot(db: AsyncSession, user: models.User):
    """
    Simulates a single "Feel Lucky" game play for a bot user.
    
    This contains the core logic from the 'feel_lucky_game' router,
    allowing us to call it directly without an HTTP request.
    """
    emojis_count = 6  # 6 emojis
    
    # The server determines the winning choice
    server_bonus_index = random.randint(0, emojis_count - 1)
    
    # The bot makes its own random choice
    bot_choice = random.randint(0, emojis_count - 1)
    
    if bot_choice == server_bonus_index:
        # --- Bot Wins ---
        try:
            new_balance = user.balance + BONUS_AMOUNT
            update_data = schemas.UserUpdate(balance=new_balance)
            await crud.update_user(db, user_id=user.id, user_update=update_data)
            
            print(f"[Bot Worker] {user.nickname} WON! New balance: {new_balance}")
            return True # Signal that an update occurred
            
        except Exception as e:
            print(f"[Bot Worker] ERROR updating balance for {user.nickname}: {e}")
            
    # else:
    #   print(f"[Bot Worker] {user.nickname} lost.")
    
    return False # No update occurred

async def run_bot(
    db_session_maker: async_sessionmaker[AsyncSession],
    manager: ConnectionManager
):
    """
    A persistent background task that simulates users playing the game.
    """
    print("--- Bot Worker is RUNNING ---")
    while True:
        try:
            # 1. Wait for a random time (e.g., 2 to 8 seconds)
            await asyncio.sleep(random.uniform(2.0, 8.0))
            
            # 2. Get a new DB session
            async with db_session_maker() as session:
            
                # 3. Find a random "bot" user (i.e., not an admin)
                all_users = await crud.get_users(session, limit=100)
                
                bot_users = [
                    user for user in all_users 
                    if user.user_type != UserType.ADMIN
                ]
                
                if not bot_users:
                    print("[Bot Worker] No bot users found to play.")
                    continue
                    
                random_user = random.choice(bot_users)
                
                # 4. Simulate the game
                update_occurred = await play_game_as_bot(session, random_user)
                
                # 5. If the game caused a change, broadcast an update
                if update_occurred:
                    await manager.broadcast({
                        "type": "leaderboard_update",
                        "user_id": random_user.id,
                        "new_balance": random_user.balance + BONUS_AMOUNT
                    })

        except asyncio.CancelledError:
            print("--- Bot is STOPPING ---")
            break
        except Exception as e:
            # Catch other errors (like DB connection issues) and wait a bit
            print(f"[Bot ] CRITICAL ERROR: {e}")
            await asyncio.sleep(15)