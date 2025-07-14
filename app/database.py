from psycopg_pool import ConnectionPool
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/mydb")

pool = ConnectionPool(conninfo=DATABASE_URL, open=True)


def fetch_flights():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM flights LIMIT 5;")
            return cur.fetchall()


def insert_booking(booking_id: str, data: dict):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO bookings (id, info) VALUES (%s, %s)", (booking_id, str(data)))
