from app.src.db.models import Reviews
from app.src.auth.service import UserService
from app.src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from app.src.reviews.schema import ReviewCreate
from fastapi import HTTPException, status
import logging


user_service = UserService()
book_service = BookService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreate,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid, session)
            user = await user_service.get_user_by_email(user_email, session)
            review_data_dict = review_data.model_dump()
            new_review = Reviews(**review_data_dict)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            new_review.user = user
            new_review.book = book

            session.add(new_review)

            await session.commit()

            return new_review

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops ... Something went wrong",
            )
