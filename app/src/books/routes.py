from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from db.database import get_session
from books.schemas import Book, BooksUpdate, BooksCreate, BookDetailsModel
from books.service import BookService
from auth.dependencies import AccessTokenBearer, RoleChecker
from errors import (
    BookNotFoundException,
)

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@book_router.get(
    "/",
    response_model=List[BookDetailsModel],
    status_code=status.HTTP_200_OK,
    dependencies=[role_checker],
)
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_uid}",
    response_model=List[BookDetailsModel],
    status_code=status.HTTP_200_OK,
    dependencies=[role_checker],
)
async def get_all_user_books(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.get(
    "/{book_uid}",
    response_model=BookDetailsModel,
    status_code=status.HTTP_200_OK,
    dependencies=[role_checker],
)
async def get_single_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book = await book_service.get_book(book_uid, session)
    # return book
    if book:
        return book
    else:
        raise BookNotFoundException()


@book_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_book(
    book_data: BooksCreate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(
        book_data,
        user_id,
        session,
    )

    return new_book


@book_router.patch(
    "/{book_uid}",
    response_model=Book,
    dependencies=[role_checker],
)
async def update_book(
    book_uid: str,
    book_update_data: BooksUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    # return updated_book

    if updated_book is None:

        raise BookNotFoundException()
    else:
        return updated_book


@book_router.delete(
    "/{book_uid}",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[role_checker],
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book_to_delete = await book_service.delete_book(book_uid, session)

    if book_to_delete is None:

        raise BookNotFoundException()

    else:
        return {}


# @book_router.get("/get_headers", status_code=200)
# def get_headers(
#     accept: str = Header(None),
#     content_type: str = Header(None),
#     user_agent: str = Header(None),
#     host: str = Header(None),
# ):
#     request_headers = {}
#     request_headers["Accept"] = accept
#     request_headers["Content-Type"] = content_type
#     request_headers["User-Agent"] = user_agent
#     request_headers["Host"] = host
#     return request_headers
