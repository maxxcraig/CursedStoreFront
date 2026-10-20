import random
import sys
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app.db import get_connection


fake = Faker()


def random_date(start_year=1995, end_year=2020):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)

    return start + timedelta(
        days=random.randint(0, (end - start).days)
    )


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python data/scripts/generate_fake_data.py COUNT"
        )

    count = int(sys.argv[1])

    with get_connection() as conn:
        category = conn.execute(
            """
            INSERT INTO categories (name)
            VALUES ('Fake')
            ON CONFLICT (name) DO UPDATE
            SET name = EXCLUDED.name
            RETURNING id
            """
        ).fetchone()

        category_id = category["id"]

        for _ in range(count):
            address = conn.execute(
                """
                INSERT INTO addresses (street, city, zip)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    fake.street_address(),
                    "San Diego",
                    fake.postcode()[:5],
                ),
            ).fetchone()

            address_id = address["id"]

            business_count = random.randint(1, 4)
            opened_on = random_date()

            for i in range(business_count):
                business = conn.execute(
                    """
                    INSERT INTO businesses (name, category_id)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (fake.company(), category_id),
                ).fetchone()

                is_last = i == business_count - 1

                if is_last and random.random() < 0.5:
                    closed_on = None
                else:
                    closed_on = opened_on + timedelta(
                        days=random.randint(180, 1800)
                    )

                conn.execute(
                    """
                    INSERT INTO occupancies (
                        address_id,
                        business_id,
                        opened_on,
                        closed_on,
                        source
                    )
                    VALUES (%s, %s, %s, %s, 'fake')
                    """,
                    (
                        address_id,
                        business["id"],
                        opened_on,
                        closed_on,
                    ),
                )

                if closed_on is not None:
                    opened_on = closed_on + timedelta(
                        days=random.randint(1, 180)
                    )

    print(f"Added {count:,} fake addresses with occupancy histories.")


if __name__ == "__main__":
    main()