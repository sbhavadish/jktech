from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Book, Review
from app.schemas import BookCreate, BookUpdate, ReviewCreate, BookOut, ReviewOut
from app.utils.auth import JWTBearer
from typing import List
from app.db import get_db

router = APIRouter()


# Add a review for a book (Authenticated)
@router.post("/books/reviews", response_model=ReviewOut, tags=["Reviews"], dependencies=[Depends(JWTBearer())])
async def add_review(
    review: ReviewCreate, 
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    book = await db.get(Book, review.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    print(user_id)
    # Use user_id["user_id"] to link the review to the current user
    new_review = Review(review_text=review.review_text, book_id=review.book_id, user_id=user_id,rating=review.rating)
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review

# Retrieve all reviews for a book (Authenticated)
@router.get("/books/{id}/reviews", response_model=List[ReviewOut], tags=["Reviews"], dependencies=[Depends(JWTBearer())])
async def get_reviews(
    id: int, 
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    result = await db.execute(select(Review).filter(Review.book_id == id))
    reviews = result.scalars().all()
    return reviews
