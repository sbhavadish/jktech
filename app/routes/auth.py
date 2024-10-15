from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.utils.auth import create_access_token
from app.utils.password import secure_pwd, verify_pwd
from app.models import User
from app.schemas import GetUser, PostUser, LoginUser
from typing import Optional

router = APIRouter()

# Register User with AsyncSession
@router.post("/register", response_model=GetUser)
async def register_user(payload: PostUser, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to register a new user.
    - Validates if the email is already registered.
    - Hashes the password and stores the user in the database.
    """
    # Query asynchronously
    result = await db.execute(select(User).filter(User.email == payload.email))
    user = result.scalar_one_or_none()
    
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = secure_pwd(payload.password)  # Hashing password
    new_user = User(email=payload.email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()  # Commit asynchronously
    await db.refresh(new_user)  # Refresh asynchronously
    return new_user

# Login User with AsyncSession
@router.post("/login")
async def login_user(payload: LoginUser, db: AsyncSession = Depends(get_db)):
    """
    Endpoint for user login.
    - Validates the user's credentials (email and password).
    - Generates an access token if credentials are valid.
    """
    # Query asynchronously
    result = await db.execute(select(User).filter(User.email == payload.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_pwd(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Generate access token asynchronously
    access_token = await create_access_token(subject=user.id, db=db)
    return {"access_token": access_token, "token_type": "bearer"}
