-- 002_schema.sql
-- Issue #11: final Phase 1 schema, built on top of 001_init.sql.
--
-- Changes:
--   categories   new lookup table, replaces the free-text businesses.category
--   businesses   fields from the city tax certificate data (account key, owner,
--                ownership type, NAICS code)
--   addresses    coordinates, plus a uniqueness rule so the loader can't
--                create the same storefront twice
--   occupancies  closed_on can't come before opened_on, and each row records
--                where it came from (seed, city, fake)
--
-- The no-overlap rule for occupancies is in 003_no_overlap.sql.

CREATE TABLE categories (
    id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

-- Move the existing free-text categories into the new table, then swap the
-- column for a foreign key. On a fresh database this just drops the column.
INSERT INTO categories (name)
SELECT DISTINCT category FROM businesses WHERE category IS NOT NULL;

ALTER TABLE businesses
    ADD COLUMN category_id    INTEGER REFERENCES categories(id),
    ADD COLUMN account_key    TEXT UNIQUE,  -- city tax certificate id, NULL for fake data
    ADD COLUMN owner_name     TEXT,
    ADD COLUMN ownership_type TEXT,
    ADD COLUMN naics_code     TEXT;

UPDATE businesses b
SET category_id = c.id
FROM categories c
WHERE c.name = b.category;

ALTER TABLE businesses DROP COLUMN category;

ALTER TABLE addresses
    ADD COLUMN lat NUMERIC(9, 6),
    ADD COLUMN lng NUMERIC(9, 6);

-- Two rows with the same street, unit and zip are the same storefront.
-- NULLS NOT DISTINCT makes unit NULL count as a value, so a building with no
-- unit can't be inserted twice.
ALTER TABLE addresses
    ADD CONSTRAINT addresses_street_unit_zip_key
    UNIQUE NULLS NOT DISTINCT (street, unit, zip);

ALTER TABLE occupancies
    ADD COLUMN source TEXT NOT NULL DEFAULT 'seed'
        CHECK (source IN ('seed', 'city', 'fake')),
    ADD CONSTRAINT occupancies_dates_check
        CHECK (closed_on IS NULL OR closed_on >= opened_on);
