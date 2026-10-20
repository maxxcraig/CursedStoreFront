-- 003_no_overlap.sql
-- Issue #12: two businesses can't occupy the same address at the same time.
--
-- Enforced in the database with an exclusion constraint: for any two rows
-- with the same address_id, their date ranges must not overlap (&&).
-- A NULL closed_on means "still open", which daterange treats as unbounded,
-- so a current tenant blocks every later start date at that address.
-- '[]' makes both ends inclusive: a business closing on the 31st and another
-- opening on the 31st still counts as an overlap.
--
-- btree_gist lets a GiST index compare plain integers (address_id) alongside
-- the range, which the constraint needs.

CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE occupancies
    ADD CONSTRAINT occupancies_no_overlap
    EXCLUDE USING gist (
        address_id WITH =,
        daterange(opened_on, closed_on, '[]') WITH &&
    );
