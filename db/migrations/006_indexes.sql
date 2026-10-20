-- 006_indexes.sql
-- Issue #14: indexes for the queries the app runs most.
-- Before and after timings are in docs/performance.md.
--
-- Numbered 006 because 005 is the staging table from issue #2.

-- Search page: WHERE street ILIKE '%text%' can't use a normal btree index,
-- because the pattern starts with a wildcard. pg_trgm indexes three-letter
-- chunks of each value, which is what ILIKE on a substring needs.
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_addresses_street_trgm
    ON addresses USING gin (street gin_trgm_ops);

CREATE INDEX idx_businesses_name_trgm
    ON businesses USING gin (name gin_trgm_ops);

-- Address page: WHERE address_id = ? ORDER BY opened_on. The exclusion
-- constraint's GiST index already finds the rows, but a btree on both
-- columns returns them already sorted, so the sort step disappears.
CREATE INDEX idx_occupancies_address_opened
    ON occupancies (address_id, opened_on);

-- Foreign key from occupancies to businesses. Postgres doesn't index
-- foreign keys on its own. Used by the search join and by any future
-- "where has this business been" page.
CREATE INDEX idx_occupancies_business
    ON occupancies (business_id);
