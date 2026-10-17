import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

#load settings from .env into environment variables
load_dotenv()


def get_connection():
    """Open a new connection to Postgres using settings from .env."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        row_factory=dict_row,
    )


def query(sql, params=None):
    """Run a SELECT and return all rows as a list of dicts."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def execute(sql, params=None):
    """Run an INSERT, UPDATE, or DELETE. Commits automatically."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)