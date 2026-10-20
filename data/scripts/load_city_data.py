"""
Load San Diego business tax certificate CSVs into the database.  (Issue #2)

Step 1 (this version): copy the raw CSV rows into staging_business_certs,
exactly as they are. Later steps move staged rows into addresses,
businesses, and occupancies, and send bad rows to load_rejects.

Usage (from the repo root, with the venv active and Docker running):
    python data/scripts/load_city_data.py data/raw/sd_businesses_active.csv data/raw/sd_businesses_inactive_2015.csv

Re-running is safe: staging is emptied first, so rows are never doubled.
"""
import csv
import os
import sys

# Let this script import app/db.py even though it lives in data/scripts/
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from app.db import get_connection  # noqa: E402

# The 27 columns in the city CSVs, in staging-table order (see docs/data.md)
CSV_COLUMNS = [
    "account_key", "account_status", "date_account_creation",
    "date_cert_expiration", "date_cert_effective", "business_owner_name",
    "ownership_type", "date_business_start", "dba_name", "naics_sector",
    "naics_code", "naics_description", "address_no", "address_pd",
    "address_road", "address_sfx", "address_no_fraction", "address_city",
    "address_state", "address_zip", "address_suite", "address_pmb_box",
    "address_po_box", "bid", "council_district", "lat", "lng",
]


def stage_file(cur, path):
    """COPY one CSV into staging_business_certs. Returns the row count."""
    source = os.path.basename(path)
    cols = ", ".join(["source_file"] + CSV_COLUMNS)
    count = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = set(CSV_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{source} is missing columns: {sorted(missing)}")
        # COPY is Postgres's bulk-load command: much faster than one INSERT per row
        with cur.copy(f"COPY staging_business_certs ({cols}) FROM STDIN") as copy:
            for row in reader:
                # Empty strings become NULL so later SQL can use IS NULL checks
                values = [source] + [(row[c].strip() or None) for c in CSV_COLUMNS]
                copy.write_row(values)
                count += 1
    return count


def main(paths):
    if not paths:
        print(__doc__)
        sys.exit(1)

    # One transaction: if any file fails, nothing is half-loaded
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE staging_business_certs RESTART IDENTITY CASCADE")
            total = 0
            for path in paths:
                n = stage_file(cur, path)
                print(f"Staged {n:,} rows from {os.path.basename(path)}")
                total += n
    print(f"Done. {total:,} rows in staging_business_certs.")


if __name__ == "__main__":
    main(sys.argv[1:])
