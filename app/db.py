from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
load_dotenv() 
db_usr = os.environ["db_usr"]
db_pwd = os.environ["db_pwd"]
db_host = os.environ["db_host"]
db_name = os.environ["db_name"]
db_port = 5432  
# Create the database engine
DATABASE_URL = f"postgresql+asyncpg://{db_usr}:{db_pwd}@{db_host}:{db_port}/{db_name}"
print(DATABASE_URL)
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

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # Dependency for database session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
