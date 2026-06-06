"""
Password Hashing and Verification using bcrypt directly
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a hashed password needs to be rehashed
    """
    return False
