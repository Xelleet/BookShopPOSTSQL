from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from starlette.middleware.cors import CORSMiddleware

DATABASE_URL = "postgresql://postgres:postgres@localhost/library_db"

app = FastAPI()
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BookCreate(BaseModel):
    title: str
    author: str
    year: int

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books4 (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                year INTEGER NOT NULL
            )
        """)
        conn.commit()
        print("Таблица создана")
    except Exception as error:
        print(f"Error: {error}")
    finally:
        cursor.close()
        conn.close()

create_table()

@app.post('/books/')
def add_book(book: BookCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO books4 (title, author, year) VALUES (%s, %s, %s) RETURNING id",
            (book.title, book.author, book.year)
        )
        book_id = cursor.fetchone()[0]
        conn.commit()
        print("Книга добавлена")
        return{"message": "Success", "book_id: ": book_id}
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

@app.get('/find_book/name/{name}/')
def find_book_name(name: str = None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        if name != "":
            sql = "SELECT * FROM books4 WHERE title ~ %s"
            cursor.execute(sql, (name,))
        else:
            sql = "SELECT * FROM books4" #Заметка: подобные конструкции любят только разработчики всяких маньячих игр про школьниц, нужно сделать по-умнее
            cursor.execute(sql)
        books = cursor.fetchall()
        if not books:
            raise HTTPException(status_code=404, detail="No books found")
        print("Книги найдены")
        return books
    except Exception as e:
        print(f"ErrorK {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        cursor.close()
        conn.close()


@app.get('/get_books/')
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT * FROM books4")
        books = cursor.fetchall()
        return books
    finally:
        cursor.close()
        conn.close()


@app.delete('/delete_book/{id}')
def delete_book(id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            "DELETE FROM books4 WHERE id = %s",
            (id,)
        )
        conn.commit()
    except Exception as error:
        print(f"Error: {error}")
    finally:
        cursor.close()
        conn.close()