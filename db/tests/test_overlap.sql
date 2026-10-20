-- test_overlap.sql
-- Proves the occupancies_no_overlap constraint from 003_no_overlap.sql works.
-- Run after the migrations and seed.sql:
--   docker exec -i cursed_db psql -U cursed -d cursed_storefronts < db/tests/test_overlap.sql
-- Every insert is rolled back, so the seed data is left as it was.

-- Case 1: a date range inside a closed occupancy is blocked.
-- Sunset Poke was at 100 Seabreeze Ave from 2017-03-01 to 2018-05-31.
DO $$
BEGIN
    INSERT INTO occupancies (address_id, business_id, opened_on, closed_on)
    SELECT a.id, b.id, '2017-09-01', '2017-12-31'
    FROM addresses a, businesses b
    WHERE a.street = '100 Seabreeze Ave' AND b.name = 'Marina Dental';
    RAISE EXCEPTION 'FAIL case 1: overlap with a closed occupancy was allowed';
EXCEPTION
    WHEN exclusion_violation THEN
        RAISE NOTICE 'PASS case 1: overlap with a closed occupancy blocked';
END $$;

-- Case 2: anything after a still-open tenant moves in is blocked.
-- Night Owl Arcade opened at 100 Seabreeze Ave on 2023-06-01 and is still there.
DO $$
BEGIN
    INSERT INTO occupancies (address_id, business_id, opened_on, closed_on)
    SELECT a.id, b.id, '2025-01-01', NULL
    FROM addresses a, businesses b
    WHERE a.street = '100 Seabreeze Ave' AND b.name = 'Marina Dental';
    RAISE EXCEPTION 'FAIL case 2: overlap with an open occupancy was allowed';
EXCEPTION
    WHEN exclusion_violation THEN
        RAISE NOTICE 'PASS case 2: overlap with an open occupancy blocked';
END $$;

-- Case 3: a gap between tenants is fine. There is nothing at 100 Seabreeze Ave
-- between Sunset Poke leaving (2018-05-31) and Tidewater Tacos arriving (2018-09-01).
BEGIN;
INSERT INTO occupancies (address_id, business_id, opened_on, closed_on)
SELECT a.id, b.id, '2018-06-15', '2018-08-15'
FROM addresses a, businesses b
WHERE a.street = '100 Seabreeze Ave' AND b.name = 'Marina Dental';
SELECT 'PASS case 3: non-overlapping occupancy allowed' AS result;
ROLLBACK;

-- Case 4: the same dates at a different address are fine.
-- Coastline Cuts has been at 340 Driftwood Ln A since 2021-02-01. The same
-- dates at the vacant 77 Harbor View Dr must be allowed.
BEGIN;
INSERT INTO occupancies (address_id, business_id, opened_on, closed_on)
SELECT a.id, b.id, '2021-02-01', NULL
FROM addresses a, businesses b
WHERE a.street = '77 Harbor View Dr' AND b.name = 'Marina Dental';
SELECT 'PASS case 4: same dates at a different address allowed' AS result;
ROLLBACK;
