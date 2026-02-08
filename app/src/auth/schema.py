from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List
from books.schemas import Book
from reviews.schema import Review


class UserCreate(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    username: str = Field(max_length=50)
    email: str = Field(max_length=50)
    password: str = Field(min_length=6)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    password_hash: str = Field(exclude=True)
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserBooksModel(UserModel):
    books: List[Book] = []
    reviews: List[Review] = []


class UserLogin(BaseModel):
    email: str
    password: str


class EmailModel(BaseModel):
    addresses: List[str] = Field(default_factory=list)


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    new_password: str
    confirm_new_password: str