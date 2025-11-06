"""
Utility functions for password hashing and verification.

This module utilizes the `passlib` library.
"""
from passlib.context import CryptContext
from typing import Final # Import for robust constant definition (optional but good practice)

# Configuration for password hashing schemes.
pwd_context: Final[CryptContext] = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password.

    Uses a timing-attack resistant comparison against the stored hash.

    Args:
        plain_password: The **plain-text password** provided by the user.
        hashed_password: The **hashed password** retrieved from the database.

    Returns:
        bool: **True** if the passwords match, **False** otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generates a secure hash for a plain-text password.

    The hash is generated using the configured schemes (e.g., bcrypt)
    and includes salt and iteration parameters automatically.

    Args:
        password: The **plain-text password** to be hashed.

    Returns:
        str: The **generated hashed password** (including algorithm, cost, and salt).
    """
    return pwd_context.hash(password)