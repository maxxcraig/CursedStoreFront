"""applies database migrations in order, skipping ones already applied.

Usage (from the project root):
    python -m db.migrate          # apply new migrations
    python -m db.migrate --seed   # apply migrations, then load seed.sql
"""
import sys
from pathlib import Path

from app.db import get_connection

DB_DIR = Path(__file__).parent
MIGRATIONS_DIR = DB_DIR / "migrations"
SEED_FILE = DB_DIR / "seed.sql"


def main():
    #table that records which migrations have already run
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename   TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)
        rows = conn.execute("SELECT filename FROM schema_migrations").fetchall()
        applied = {row["filename"] for row in rows}

    #run each new migration in its own transaction, in filename order
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        print(f"Applying {path.name} ...")
        with get_connection() as conn:
            conn.execute(path.read_text())
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (%s)",
                (path.name,),
            )

    if "--seed" in sys.argv:
        print("Loading seed.sql ...")
        with get_connection() as conn:
            conn.execute(SEED_FILE.read_text())

    print("Database is up to date.")


if __name__ == "__main__":
    main()