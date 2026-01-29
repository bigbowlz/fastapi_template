from typing import Optional
from datetime import date
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

BOOKS = []


@app.get("/", status_code=status.HTTP_200_OK)
async def hello():
    return "Hello Wanli!"


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def get_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book
    return HTTPException(status_code=404, detail="Item not found.")


@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)

    return books_to_return


@app.get(
    "/books/filter_by_date/{start_date}/{end_date}", status_code=status.HTTP_200_OK
)
async def get_books_by_date_range(
    start_date: date = Path(gt=date(1900, 1, 1)),
    end_date: date = Path(lt=date(2500, 1, 1)),
):
    books_to_return = []
    for book in BOOKS:
        if book.publish_date > start_date and book.publish_date < end_date:
            books_to_return.append(book)
    return books_to_return


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    publish_date: date

    def __init__(self, id, title, author, description, rating, publish_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.publish_date = publish_date


BOOKS = [
    Book(
        1,
        "Computer Science Pro",
        "codingwithroby",
        "A very nice book!",
        5,
        date(2020, 1, 5),
    ),
    Book(
        2,
        "Be Fast with FastAPI",
        "codingwithroby",
        "A great book!",
        5,
        date(2015, 1, 5),
    ),
    Book(
        3,
        "Master Endpoints",
        "codingwithroby",
        "A awesome book!",
        5,
        date(2009, 1, 5),
    ),
    Book(
        4,
        "HP1",
        "Author 1",
        "Book Description",
        2,
        date(1998, 1, 5),
    ),
    Book(
        5,
        "HP2",
        "Author 2",
        "Book Description",
        3,
        date(1990, 1, 5),
    ),
    Book(
        6,
        "HP3",
        "Author 3",
        "Book Description",
        1,
        date(1985, 1, 5),
    ),
]


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create.", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    publish_date: date

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "An author",
                "description": "Some descriptions",
                "rating": 3,
                "publish_date": "1995-06-01",
            }
        }
    }


@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(assign_book_id(new_book))


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(updated_book: BookRequest):
    book_changed = 0
    for i in range(len(BOOKS)):
        if BOOKS[i].id == updated_book.id:
            BOOKS[i] = Book(**updated_book.model_dump())
            book_changed = 1
    if not book_changed:
        return HTTPException(status_code=404, detail="No book found to update.")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    BOOKS_copy = BOOKS.copy()
    for i in range(len(BOOKS_copy)):
        if BOOKS_copy[i].id == book_id:
            BOOKS.pop(i)


def assign_book_id(book: Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    return book
