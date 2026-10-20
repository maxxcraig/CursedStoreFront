from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.db import get_connection

RAW_DIR = PROJECT_ROOT / "data" / "raw"


def stage_csvs():
    files = sorted(RAW_DIR.glob("sd_businesses*_datasd.csv"))

    if not files:
        raise SystemExit("No City CSV files found in data/raw/")

    with get_connection() as conn:
        conn.execute("TRUNCATE city_business_staging")
        conn.execute("TRUNCATE load_rejects RESTART IDENTITY")

        for path in files:
            print(f"Loading {path.name} ...")

            with path.open("r", encoding="utf-8-sig") as f:
                with conn.cursor() as cur:
                    with cur.copy(
                        """
                        COPY city_business_staging
                        FROM STDIN
                        WITH (FORMAT CSV, HEADER TRUE)
                        """
                    ) as copy:
                        while chunk := f.read(1024 * 1024):
                            copy.write(chunk)


def transform():
    sql = (PROJECT_ROOT / "data" / "scripts" / "load_city_data.sql").read_text()

    with get_connection() as conn:
        conn.execute(sql)


def summary():
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM city_business_staging) AS staged,
                (SELECT COUNT(*) FROM occupancies
                 WHERE source = 'city') AS occupancies,
                (SELECT COUNT(*) FROM load_rejects) AS rejects
            """
        ).fetchone()

    print()
    print(f"Staged rows:      {row['staged']:,}")
    print(f"City occupancies: {row['occupancies']:,}")
    print(f"Rejected rows:    {row['rejects']:,}")


def main():
    stage_csvs()
    transform()
    summary()


if __name__ == "__main__":
    main()