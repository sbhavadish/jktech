from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Integer, Float, UUID, Identity
from sqlalchemy.orm import relationship
from app.db import Base


# User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Identity(start=1), primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Relationship to Token model
    tokens = relationship("Token", back_populates="user")


# Token model
class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, Identity(start=1), primary_key=True, index=True)
    token = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationship to User model
    user = relationship("User", back_populates="tokens")


# Book model
class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, Identity(start=1), primary_key=True, index=True)
    title = Column(String(255), index=True)
    author = Column(String(255), index=True)
    genre = Column(String(100), index=True)
    year_published = Column(Integer)
    summary = Column(Text)

    # Relationship to the Review model
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")


# Review model
class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, Identity(start=1), primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))  # Foreign key to User's id field
    review_text = Column(Text)
    rating = Column(Float)

    # Relationship to the Book model
    book = relationship("Book", back_populates="reviews")

    # Relationship to the User model (who wrote the review)
    user = relationship("User")
