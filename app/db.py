import os
import sys
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

# Load environment variables
load_dotenv()

# Retrieve environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
# Create the database engine

print("Connecting to database:", DATABASE_URL)  # Debugging

# Define the Base class
Base = declarative_base()

# Create asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create an async session factory
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Dependency to get the async database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        await session.close()
