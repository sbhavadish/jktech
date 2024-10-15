import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch
from main import app
from app.db import Base, engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User

# Database setup and teardown fixture
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Async client fixture
@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Token fixture to authenticate requests
@pytest_asyncio.fixture(scope="function")
async def auth_headers(async_client):
    # First, register a user and log in to get the token
    payload = {"email": "testuser12@example.com", "password": "securepassword"}
    await async_client.post("/register", json=payload)
    
    login_payload = {"email": payload["email"], "password": payload["password"]}
    response = await async_client.post("/login", json=login_payload)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

# Test for registering a user
@pytest.mark.asyncio
async def test_register_user(async_client):
    payload = {"email": "testuser10@example.com", "password": "securepassword"}
    response = await async_client.post("/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]

    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).filter(User.email == payload["email"]))
        user = result.scalar_one_or_none()
        assert user is not None

# Test for logging in a user and retrieving access token
@pytest.mark.asyncio
async def test_login_user(async_client):
    payload = {"email": "testuser80@example.com", "password": "securepassword"}
    await async_client.post("/register", json=payload)

    login_payload = {"email": payload["email"], "password": payload["password"]}
    response = await async_client.post("/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# Test for creating a book
@pytest.mark.asyncio
async def test_create_book(async_client: AsyncClient, auth_headers):
    payload = {
        "title": "New Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2021,
        "summary": "A brief summary of the book"
    }
    response = await async_client.post("/books/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == payload["title"]

# Test for retrieving all books
@pytest.mark.asyncio
async def test_get_books(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/books/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Test for retrieving a single book by ID
@pytest.mark.asyncio
async def test_get_book(async_client: AsyncClient, auth_headers):
    # First, create a book
    payload = {
        "title": "New Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2021,
        "summary": "A brief summary of the book"
    }
    response = await async_client.post("/books/", json=payload, headers=auth_headers)
    book_id = response.json()["id"]
    
    # Now, retrieve the book
    response = await async_client.get(f"/books/{book_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id

# Test for updating a book
@pytest.mark.asyncio
async def test_update_book(async_client: AsyncClient, auth_headers):
    # First, create a book
    payload = {
        "title": "New Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2021,
        "summary": "A brief summary of the book"
    }
    response = await async_client.post("/books/", json=payload, headers=auth_headers)
    book_id = response.json()["id"]
    
    # Now, update the book
    update_payload = {"title": "Updated Title"}
    response = await async_client.put(f"/books/{book_id}", json=update_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"

# Test for deleting a book
@pytest.mark.asyncio
async def test_delete_book(async_client: AsyncClient, auth_headers):
    # First, create a book
    payload = {
        "title": "New Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2021,
        "summary": "A brief summary of the book"
    }
    response = await async_client.post("/books/", json=payload, headers=auth_headers)
    book_id = response.json()["id"]
    
    # Now, delete the book
    response = await async_client.delete(f"/books/{book_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Book deleted successfully"

# Test for getting book summary and average rating
@pytest.mark.asyncio
async def test_get_summary(async_client: AsyncClient, auth_headers):
    # First, create a book
    payload = {
        "title": "New Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2021,
        "summary": "A brief summary of the book"
    }
    response = await async_client.post("/books/", json=payload, headers=auth_headers)
    book_id = response.json()["id"]
    
    # Now, get summary and rating
    response = await async_client.get(f"/books/{book_id}/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == payload["summary"]
    assert data["average_rating"] is None

# Test for adding a review to a book
@pytest.mark.asyncio
async def test_add_review(async_client: AsyncClient, auth_headers):
    # First, create a book to review
    book_payload = {
        "title": "New Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2021,
        "summary": "A brief summary of the book"
    }
    book_response = await async_client.post("/books/", json=book_payload, headers=auth_headers)
    book_id = book_response.json()["id"]

    # Now, add a review for the book
    review_payload = {
        "review_text": "Great book!",
        "rating": 5,
        "book_id": book_id,
        "user_id": 1  # Assuming a valid user_id
    }
    review_response = await async_client.post("/books/reviews", json=review_payload, headers=auth_headers)
    assert review_response.status_code == 200
    data = review_response.json()
    assert data["review_text"] == review_payload["review_text"]
    assert data["rating"] == review_payload["rating"]
    assert data["book_id"] == book_id

# Test for retrieving all reviews for a book
@pytest.mark.asyncio
async def test_get_reviews(async_client: AsyncClient, auth_headers):
    # First, create a book
    book_payload = {
        "title": "New Book",
        "author": "John Doe",
        "genre": "Fiction",
        "year_published": 2021,
        "summary": "A brief summary of the book"
    }
    book_response = await async_client.post("/books/", json=book_payload, headers=auth_headers)
    book_id = book_response.json()["id"]

    # Add a review for the book
    review_payload = {
        "review_text": "Amazing read!",
        "rating": 5,
        "book_id": book_id,
        "user_id": 1  # Assuming user_id=1
    }
    await async_client.post("/books/reviews", json=review_payload, headers=auth_headers)

    # Retrieve all reviews for the book
    response = await async_client.get(f"/books/{book_id}/reviews", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Assertions to verify that the correct reviews are returned
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["review_text"] == review_payload["review_text"]
    assert data[0]["rating"] == review_payload["rating"]
    assert data[0]["book_id"] == book_id


# Test for generating summary from PDF
@pytest.mark.asyncio
async def test_generate_summary(async_client: AsyncClient, auth_headers):
    file_path = r"Books\rider5.pdf"
    with open(file_path, "rb") as file:
        response = await async_client.post("/generate-summary", files={"file": ("file.pdf", file)}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "final_summary" in data

# Test for getting book recommendations
@pytest.mark.asyncio
async def test_get_recommendations(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)