"""Fill the database with fake addresses, businesses and occupancies
for the performance check in issue 14 (docs/performance.md). This is only for
timings; the real fake data generator is issue 4. Occupancies at one address never overlap,
so the exclusion constraint accepts them.

Usage (from the repo root, with the venv active and migrations applied):
    python db/tests/perf_fake_data.py 200000      # number of addresses
"""
import random
import sys
from datetime import date, timedelta

from faker import Faker

sys.path.insert(0, ".")
from app.db import get_connection  # noqa: E402

N_ADDRESSES = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000
random.seed(14)
fake = Faker()
Faker.seed(14)

CATEGORIES = ["Restaurant", "Bar", "Fitness", "Retail", "Healthcare", "Salon",
              "Entertainment", "Cafe", "Grocery", "Office"]
SUFFIXES = ["Cafe", "Tacos", "Market", "Studio", "Grill", "Books", "Dental",
            "Yoga", "Barbers", "Pizza", "Nails", "Hardware", "Boba", "Sushi"]
ZIPS = ["92101", "92102", "92103", "92104", "92105", "92106", "92107", "92108",
        "92109", "92110", "92111", "92113", "92115", "92116", "92117"]


def main():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO categories (name) VALUES " +
                    ",".join(f"('{c}')" for c in CATEGORIES) + " ON CONFLICT DO NOTHING")
        cur.execute("SELECT id FROM categories")
        cat_ids = [r["id"] for r in cur.fetchall()]

        print(f"addresses: {N_ADDRESSES:,}")
        seen = set()
        with cur.copy("COPY addresses (street, unit, zip) FROM STDIN") as cp:
            while len(seen) < N_ADDRESSES:
                street = f"{random.randint(1, 9999)} {fake.street_name()}"
                unit = random.choice([None, None, None, "A", "B", "1", "2"])
                row = (street, unit, random.choice(ZIPS))
                if row in seen:
                    continue
                seen.add(row)
                cp.write_row(row)
        cur.execute("SELECT id FROM addresses WHERE id > 6 ORDER BY id")
        addr_ids = [r["id"] for r in cur.fetchall()]

        # Each address gets 1 to 8 tenants in sequence with gaps between them.
        plan = []  # (address_id, opened_on, closed_on)
        for aid in addr_ids:
            day = date(1995, 1, 1) + timedelta(days=random.randint(0, 365 * 10))
            for _ in range(random.choices(range(1, 9), weights=[30, 25, 15, 10, 8, 6, 4, 2])[0]):
                opened = day
                closed = opened + timedelta(days=random.randint(90, 365 * 8))
                if closed >= date(2026, 10, 1):
                    plan.append((aid, opened, None))
                    break
                plan.append((aid, opened, closed))
                day = closed + timedelta(days=random.randint(1, 400))
                if day >= date(2026, 10, 1):
                    break

        print(f"businesses: {len(plan):,}")
        with cur.copy("COPY businesses (name, category_id) FROM STDIN") as cp:
            for _ in plan:
                cp.write_row((f"{fake.last_name()} {random.choice(SUFFIXES)}", random.choice(cat_ids)))
        cur.execute("SELECT id FROM businesses WHERE id > 11 ORDER BY id")
        biz_ids = [r["id"] for r in cur.fetchall()]

        print(f"occupancies: {len(plan):,}")
        with cur.copy("COPY occupancies (address_id, business_id, opened_on, closed_on, source) FROM STDIN") as cp:
            for bid, (aid, opened, closed) in zip(biz_ids, plan):
                cp.write_row((aid, bid, opened, closed, "fake"))
        cur.execute("ANALYZE")
    print("done")


main()
