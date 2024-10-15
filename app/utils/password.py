# app/utils/password.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def secure_pwd(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_pwd(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
