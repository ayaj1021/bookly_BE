from fastapi import FastAPI
from contextlib import asynccontextmanager
from books.routes import book_router
from auth.routes import auth_router
from reviews.routes import review_router
from db.database import init_db
from errors import register_all_errors
from middleware import register_middleware


@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is starting....")
    await init_db()
    yield
    print("Server has been stopped")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
    # We can comment out life span event once we start using alembic
    # lifespan=life_span
)


register_all_errors(app)

register_middleware(app)


app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Authentication"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["Reviews"])
