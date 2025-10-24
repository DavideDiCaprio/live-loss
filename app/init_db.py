from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from faker import Faker
import random
import os
import asyncio

# Use absolute imports for consistency
from app import crud, schemas, models
from app.models import UserType
from app.database import engine, Base, DATABASE_URL

fake = Faker()

async def run_app_setup(db_session_maker: async_sessionmaker[AsyncSession], num_users: int = 15):
    """
    Handles the complete database setup: cleanup, table creation, and initial seeding.
    This logic is extracted from app/main.py's lifespan function.
    """
    db_file = "test.db"
    # Logic to remove old database file (for local SQLite development)
    if "sqlite" in DATABASE_URL and db_file in DATABASE_URL:
        if os.path.exists(db_file):
            print(f"Removing old database file: {db_file}")
            os.remove(db_file)
            
    # Create tables
    async with engine.begin() as conn:
        print("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed data
    print("Starting database seeding...")
    await create_random_users(db_session_maker, num_users=num_users)
    
    print("Database setup complete.")


async def create_random_users(db_session_maker: async_sessionmaker[AsyncSession], num_users: int = 10):
    """
    Creates a specified number of random users in the database.
    """
    print(f"--- Seeding database with {num_users} random users... ---")
    
    async with db_session_maker() as session:
        for i in range(num_users):
            email = fake.unique.email()
            nickname = fake.unique.user_name()
            password = "Password123" 
            
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
                # Log the specific exception to help debugging if seeding fails
                print(f"Error creating user {email}: {type(e).__name__} - {e}")
                await session.rollback()

    print("--- Database seeding complete. ---")
