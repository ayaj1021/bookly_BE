from sqlmodel.ext.asyncio.session import AsyncSession
from books.schemas import BooksCreate, BooksUpdate
from db.models import Book
from sqlmodel import select, desc


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )

        result = await session.exec(statement)

        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)

        result = await session.exec(statement)

        book = result.first()

        return book if book is not None else None

        # return result.first()

    async def create_book(
        self, book_data: BooksCreate, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_data.model_dump()

        new_book = Book(**book_data_dict)

        # new_book.published_date = datetime.strptime(
        #     book_data_dict["published_date"], "%Y-%m-%d"
        # )

        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_uid: str, book_data: BooksUpdate, session: AsyncSession
    ):
        # statement = select(Book).where(Book.uid == book_uid)

        # if not statement:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Book with {book_uid} is not found",
        #     )

        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:

            update_data_dict = book_data.model_dump()

            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()

            return book_to_update

        else:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        # statement = select(Book).where(Book.uid == book_uid)

        # if not statement:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"Book with {book_uid} is not found",
        #     )

        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete is not None:

            await session.delete(book_to_delete)

            await session.commit()

            return {}

        else:
            return None
