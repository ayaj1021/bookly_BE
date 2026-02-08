from fastapi import APIRouter, Depends, status
from reviews.service import ReviewService
from sqlmodel.ext.asyncio.session import AsyncSession
from reviews.schema import ReviewCreate, Review
from auth.dependencies import get_current_user
from db.models import User
from db.database import get_session

review_service = ReviewService()

review_router = APIRouter()


@review_router.post(
    "/book/{book_uid}", response_model=Review, status_code=status.HTTP_201_CREATED
)
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )

    return new_review
