from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from faker import Faker
import random
import asyncio

from . import crud, schemas, models
from .models import UserType

fake = Faker()

async def create_random_users(db_session_maker: async_sessionmaker[AsyncSession], num_users: int = 10):
    """
    Creates a specified number of random users in the database.
    """
    print(f"--- Seeding database with {num_users} random users... ---")
    
    async with db_session_maker() as session:
        for i in range(num_users):
            email = fake.unique.email()
            nickname = fake.unique.user_name()
            password = "password123" # Default password for all
            
            user_in = schemas.UserCreate(
                email=email,
                password=password,
                nickname=nickname,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                age=random.randint(18, 70)
            )
            
            try:
                db_user = await crud.create_user(session, user_in)
                
                update_data = schemas.UserUpdate(
                    balance=round(random.uniform(0.0, 5000.0), 2),
                    user_type=random.choice(list(UserType))
                )
                await crud.update_user(session, user_id=db_user.id, user_update=update_data)
                
                print(f"Created user: {db_user.nickname} ({db_user.email})")

            except Exception as e:
                print(f"Error creating user {email}: {e}")
                await session.rollback()

    print("--- Database seeding complete. ---")
