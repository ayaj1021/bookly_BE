from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class ReviewCreate(BaseModel):
    review_text: str
    rating: int


class Review(BaseModel):
    uid: uuid.UUID
    rating: int = Field(lt=5)
    review_text: str
    user_uid: Optional[uuid.UUID]
    book_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
