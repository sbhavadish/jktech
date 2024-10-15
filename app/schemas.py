from pydantic import BaseModel, EmailStr
from typing import Optional, List

class GetUser(BaseModel):
    email: EmailStr

    class Config:
        from_attributes  = True

class LoginUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes  = True

class PostUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes  = True



# Book Schema for Creating a New Book
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int
    summary: Optional[str] = None

# Book Schema for Output (Retrieving Book Information)
class BookOut(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    year_published: int
    summary: Optional[str] = None

    class Config:
        from_attributes  = True

# Book Schema for Updating Book Information
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    year_published: Optional[int] = None
    summary: Optional[str] = None

# Review Schema for Creating a Review
class ReviewCreate(BaseModel):
    book_id: int
    review_text: str
    rating: float

# Review Schema for Output (Retrieving Review Information)
class ReviewOut(BaseModel):
    id: int
    book_id: int
    review_text: str
    rating: float

    class Config:
        from_attributes  = True

class Recommendation(BaseModel):
    book_id: int
    summary: Optional[str] = None
    recommendation: Optional[str] = None