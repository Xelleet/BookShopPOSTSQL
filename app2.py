from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:postgres@localhost/library_db"

app = FastAPI()

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
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARHCAR(255) NOT NULL,
                author INTEGER NOT NULL
            )
        """)
        conn.commit()
        print("Таблица создана")
    except Exception as error:
        print(f"Error: {error}")
    finally:
        cursor.close()
        conn.close()

@app.post('/books/')
def add_book(book: BookCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO books (title, author, year) VALUES (book.title, book.author, book.year) RETURNING od")
        book_id = cursor.fetchone()[0]
        conn.commit()
        print("Книга добавлена")
        return{"message": "Success", "book_id: ": book_id}
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()