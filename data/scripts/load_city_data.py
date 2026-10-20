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
                        COPY city_business_staging(
                            account_key,
                            account_status,
                            date_account_creation,
                            date_cert_expiration,
                            date_cert_effective,
                            business_owner_name,
                            ownership_type,
                            date_business_start,
                            dba_name,
                            naics_sector,
                            naics_code,
                            naics_description,
                            address_no,
                            address_pd,
                            address_road,
                            address_sfx,
                            address_no_fraction,
                            address_city,
                            address_state,
                            address_zip,
                            address_suite,
                            address_pmb_box,
                            address_po_box,
                            bid,
                            council_district,
                            lat,
                            lng
                        )
                        FROM STDIN
                        WITH (FORMAT CSV, HEADER TRUE)
                        """
                    ) as copy:
                        while chunk := f.read(1024 * 1024):
                            copy.write(chunk)

def clean_addresses():
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE city_business_staging
            SET
                clean_street = INITCAP(
                    BTRIM(
                        CONCAT_WS(
                            ' ',
                            NULLIF(BTRIM(address_no), ''),
                            NULLIF(BTRIM(address_pd), ''),
                            NULLIF(BTRIM(address_road), ''),
                            NULLIF(BTRIM(address_sfx), '')
                        )
                    )
                ),
                clean_unit = NULLIF(BTRIM(address_suite), '')
            """
        )

        conn.execute(
            """
            UPDATE city_business_staging
            SET clean_street =
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(
                                    clean_street,
                                    '\\s+Street$', ' St', 'i'
                                ),
                                '\\s+Avenue$', ' Ave', 'i'
                            ),
                            '\\s+Road$', ' Rd', 'i'
                        ),
                        '\\s+Boulevard$', ' Blvd', 'i'
                    ),
                    '\\s+Drive$', ' Dr', 'i'
                )
            """
        )
                
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
    clean_addresses()
    transform()
    summary()


if __name__ == "__main__":
    main()