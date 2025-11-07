from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from faker import Faker
import random
import os
import asyncio

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
    
    # 1. Create the default Admin User
    await create_admin_user(db_session_maker)
    
    # 2. Seed random users
    await create_random_users(db_session_maker, num_users=num_users)
    
    print("Database setup complete.")


async def create_admin_user(db_session_maker: async_sessionmaker[AsyncSession]):
    """
    Creates a default admin user if one does not already exist.
    """
    print("--- Checking for Admin user... ---")
    admin_email = "admin"
    admin_pass  = "admin" 
    admin_nick  = "AdminUser"
    
    async with db_session_maker() as session:
        # Check if admin user already exists
        existing_admin = await crud.get_user_by_email(session, email=admin_email)
        if existing_admin:
            print(f"Admin user ({admin_email}) already exists. Skipping creation.")
            return

        # Create the admin user
        print(f"Creating default admin user: {admin_email}")
        try:
            admin_in = schemas.UserCreate(
                email=admin_email,
                password=admin_pass,
                nickname=admin_nick,
                first_name="Admin",
                last_name="User",
                age=99
            )
            db_user = await crud.create_user(session, admin_in)
            
            # Update the user to be an Admin and give them a starting balance
            admin_update = schemas.UserUpdate(
                balance=9999.99,
                user_type=models.UserType.ADMIN,
                is_active=True # Ensure they are active
            )
            await crud.update_user(session, user_id=db_user.id, user_update=admin_update)
            
            print(f"Successfully created admin user: {db_user.nickname}")
            print(f"Admin Login: {admin_email} / {admin_pass}")

        except Exception as e:
            print(f"CRITICAL: Error creating admin user {admin_email}: {type(e).__name__} - {e}")
            await session.rollback()


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
                nickname=nickname
            )
            
            try:
                if await crud.get_user_by_email(session, email) or await crud.get_user_by_nickname(session, nickname):
                    print(f"Skipping duplicate user: {nickname}")
                    continue

                db_user = await crud.create_user(session, user_in)
                
                update_data = schemas.UserUpdate(
                    balance=round(random.uniform(0.0, 5000.0), 2),
                    user_type=random.choice([ut for ut in UserType if ut != UserType.ADMIN]) # Don't create random admins
                )
                await crud.update_user(session, user_id=db_user.id, user_update=update_data)
                
                print(f"Created user: {db_user.nickname} ({db_user.email})")

            except Exception as e:
                print(f"Error creating user {email}: {type(e).__name__} - {e}")
                await session.rollback()

    print("--- Database seeding complete. ---")