from pydantic import BaseModel
from datetime import datetime, date
from reviews.schema import Review
import uuid
from typing import List



class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


    # class Config:
    #         from_attributes = True

class BookDetailsModel(Book):
    reviews: List[Review] = []


class BooksUpdate(BaseModel):
    title: str
    publisher: str
    page_count: int
    language: str


class BooksCreate(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
    published_date: date