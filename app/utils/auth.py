import jwt
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models import Token, User
from dotenv import load_dotenv
import os
import sys
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Load environment variables
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
load_dotenv()
secret_key = os.environ["secret_key"]
algorithm = os.environ["algorithm"]

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: AsyncSession = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            token = credentials.credentials
            if not await self.verify_jwt(token, db):
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return await self.extract_user_from_jwt(token)
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    # Asynchronous JWT verification
    async def verify_jwt(self, token: str, db: AsyncSession) -> bool:
        try:
            # Decode the token with the secret key and check if it's expired
            decoded_token = jwt.decode(token, secret_key, algorithms=[algorithm])

            # Optional: Print decoded token for debugging purposes
            print(f"Decoded Token: {decoded_token}")

            # Asynchronously retrieve token from the database and verify its existence
            result = await db.execute(select(Token).filter(Token.token == token))
            db_token = result.scalar_one_or_none()

            if db_token is None:
                print(f"Token passed in header: {token}")  # Debugging: Print passed token
                print("Token not found in database.")  # Debugging: Token not found
                raise HTTPException(status_code=403, detail="Token not found in database.")

            return True  # If token is valid and found in the database
        except ExpiredSignatureError:
            # Handle expired token
            raise HTTPException(status_code=401, detail="Token has expired")
        except InvalidTokenError:
            # Handle invalid token signature
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            # Catch any other exception for debugging purposes
            print(f"Exception in token verification: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

    async def extract_user_from_jwt(self, token: str):
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return int(payload.get("sub"))  # Assuming "sub" contains user identification info
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# Create access token with async database interaction
async def create_access_token(subject: str, db: AsyncSession, expires_delta: int = None) -> str:
    expires = datetime.utcnow() + timedelta(minutes=expires_delta) if expires_delta else datetime.utcnow() + timedelta(minutes=30)
    to_encode = {"exp": expires, "sub": str(subject)}
    token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    
    # Asynchronously save the token to the database
    db_token = Token(token=token, user_id=subject)
    db.add(db_token)
    await db.commit()  # Use await for async commit

    print(f"Token saved in the database: {token}")  # Debugging: Print token

    return token
