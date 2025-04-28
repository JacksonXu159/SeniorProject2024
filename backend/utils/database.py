from psycopg2 import pool
from dotenv import load_dotenv
import os

load_dotenv()

PGHOST = os.getenv("PGHOST")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
ENDPOINT = os.getenv("ENDPOINT")

try:
    connection_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=PGHOST,
        database=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
        port=5432,
        sslmode="require",
        options=f"endpoint={ENDPOINT}"  # This fixes the SNI error
    )

    if connection_pool:
        print("Connection pool created successfully")

except Exception as e:
    print(f"Error creating connection pool: {e}")

def get_db():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
