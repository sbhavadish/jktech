from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Book, Review
from app.schemas import BookCreate, BookUpdate, BookOut,Recommendation
from app.utils.auth import JWTBearer
from typing import List
from app.db import get_db
from app.utils.helper import *
import os
router = APIRouter()

# Add a new book (Authenticated)
@router.post("/books/", response_model=BookOut, tags=["Books"], dependencies=[Depends(JWTBearer())])
async def create_book(
    book: BookCreate, 
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    new_book = Book(**book.dict())
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book

# Retrieve all books (Authenticated)
@router.get("/books/", response_model=List[BookOut], tags=["Books"], dependencies=[Depends(JWTBearer())])
async def get_books(
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    result = await db.execute(select(Book))
    books = result.scalars().all()
    return books

# Retrieve a specific book by ID (Authenticated)
@router.get("/books/{id}", response_model=BookOut, tags=["Books"], dependencies=[Depends(JWTBearer())])
async def get_book(
    id: int, 
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    book = await db.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Update a book's information by ID (Authenticated)
@router.put("/books/{id}", response_model=BookOut, tags=["Books"], dependencies=[Depends(JWTBearer())])
async def update_book(
    id: int, 
    book_update: BookUpdate, 
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    book = await db.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_update.dict(exclude_unset=True).items():
        setattr(book, key, value)
    await db.commit()
    await db.refresh(book)
    return book

# Delete a book by ID (Authenticated)
@router.delete("/books/{id}", response_model=dict, tags=["Books"], dependencies=[Depends(JWTBearer())])
async def delete_book(
    id: int, 
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    book = await db.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    await db.delete(book)
    await db.commit()
    return {"message": "Book deleted successfully"}


# Get a summary and aggregated rating for a book (Authenticated)
@router.get("/books/{id}/summary", tags=["Books"], dependencies=[Depends(JWTBearer())])
async def get_summary(
    id: int, 
    db: AsyncSession = Depends(get_db), 
    user_id: int = Depends(JWTBearer())
):
    book = await db.get(Book, id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    result = await db.execute(select(Review).filter(Review.book_id == id))
    reviews = result.scalars().all()

    if not reviews:
        return {"summary": book.summary, "average_rating": None}

    avg_rating = sum([review.rating for review in reviews]) / len(reviews)
    return {"summary": book.summary, "average_rating": avg_rating}



# Generate a summary for a given book content (Authenticated)
@router.post("/generate-summary", tags=["Books"], dependencies=[Depends(JWTBearer())])
async def generate_summary(
    file: UploadFile = File(...), 
    user_id: int = Depends(JWTBearer())
):
    # Placeholder for AI model interaction to generate summary
    """Endpoint to upload a PDF file and get a short summary of the book."""
    if file.filename.endswith(".pdf"):
        # Save the PDF file locally
        pdf_file_path = f"temp_{file.filename}"
        with open(pdf_file_path, "wb") as temp_file:
            temp_file.write(file.file.read())
        print('Step 1')
        # Step 1: Try direct text extraction using PyPDF2
        extracted_text = extract_text_from_pdf_using_pypdf2(pdf_file_path)
        print('Step 2')
        # Step 2: If direct text extraction fails, fall back to OCR
        if not extracted_text:
            extracted_text = extract_text_from_pdf_using_ocr(pdf_file_path)
            print('Step 2 not')
        # Step 3: Handle large text by splitting into smaller chunks if needed
        final_summary = None
        if len(extracted_text) > CHARACTER_LIMIT:
            full_summary = handle_large_text(extracted_text)
            final_summary = generate_short_summary(full_summary)
        else:
            final_summary = generate_short_summary(extracted_text)
        print('Step 3')
        # Step 4: Send the full_summary to Llama 3 again for further summarization
        
        print('Step 4')
        print(final_summary)
        # Clean up the temporary file
        os.remove(pdf_file_path)

        return {"final_summary": final_summary}
    else:
        return {"error": "Please upload a PDF file"}

# Get book recommendations (Authenticated)
@router.get("/recommendations",response_model=List[Recommendation], tags=["Books"], dependencies=[Depends(JWTBearer())])
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(JWTBearer())
):
    """
    Fetches the user's reviews and all books, sends them to Llama for personalized book recommendations.
    """
    try:

        # Step 1: Fetch all reviews of the user
        result = await db.execute(select(Review).filter(Review.user_id == user_id))
        user_reviews = result.scalars().all()

        if not user_reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this user")

        # Prepare user reviews for Llama
        user_reviews_data = [
            {
                "book_id": review.book_id,
                "review_text": review.review_text
            }
            for review in user_reviews
        ]

        # Step 2: Fetch all books
        result_books = await db.execute(select(Book))
        books = result_books.scalars().all()

        if not books:
            raise HTTPException(status_code=404, detail="No books found")

        # Prepare book summaries for Llama
        books_data = [
            {
                "book_id": book.id,
                "summary": book.summary
            }
            for book in books
        ]

        # Step 3: Send user reviews and book summaries to Llama for recommendations
        recommendation = get_llama_recommendations(user_reviews_data, books_data)
        book_id = 0
        recommended_books =[{
                    "book_id": None,
                    "summary": None,
                    "recommendation":"No Recommendation"
                }]
        if  recommendation:
            book_id = recommendation[0]["book_id"]
            if book_id > 0:
                recommended_books =[{
                        "book_id": book.id,
                        "summary": book.summary,
                        "recommendation":"I hope this book meets your preferences and fulfills your expectations."
                    }
                    for book in books if book.id == book_id]
        # Return the recommended book IDs or titles
        return recommended_books

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
