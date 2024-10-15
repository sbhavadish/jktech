from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.books import router as books_router
from app.routes.reviews import router as reviews_router
from sqlalchemy.ext.asyncio import AsyncEngine
from app.db import engine, Base
from contextlib import asynccontextmanager

# Create the database tables with lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the engine is an AsyncEngine
    if isinstance(engine, AsyncEngine):
        async with engine.begin() as conn:
            # Create database tables
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Add any cleanup logic here if necessary

# Create the FastAPI app with the lifespan context
app = FastAPI(lifespan=lifespan)

# Include the authentication routes
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(reviews_router)

# Main entry point to run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
