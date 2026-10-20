-- 005_staging.sql
-- Issue #2: tables used by data/scripts/load_city_data.py
--
-- staging_business_certs holds the raw city CSV exactly as downloaded.
-- Every column is TEXT on purpose: the city data has bad dates (year 0002,
-- 5201, etc., see docs/data.md), so typing them here would make the whole
-- load fail. We clean and convert later, when moving rows into the real tables.

CREATE TABLE staging_business_certs (
    id                    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_file           TEXT NOT NULL,   -- which CSV the row came from
    account_key           TEXT,
    account_status        TEXT,
    date_account_creation TEXT,
    date_cert_expiration  TEXT,
    date_cert_effective   TEXT,
    business_owner_name   TEXT,
    ownership_type        TEXT,
    date_business_start   TEXT,
    dba_name              TEXT,
    naics_sector          TEXT,
    naics_code            TEXT,
    naics_description     TEXT,
    address_no            TEXT,
    address_pd            TEXT,
    address_road          TEXT,
    address_sfx           TEXT,
    address_no_fraction   TEXT,
    address_city          TEXT,
    address_state         TEXT,
    address_zip           TEXT,
    address_suite         TEXT,
    address_pmb_box       TEXT,
    address_po_box        TEXT,
    bid                   TEXT,
    council_district      TEXT,
    lat                   TEXT,
    lng                   TEXT
);

-- Rows that can't be turned into a valid occupancy (bad dates, missing
-- address, overlapping another business at the same address) go here with a
-- reason, instead of crashing the load script.
CREATE TABLE load_rejects (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    staging_id  INTEGER REFERENCES staging_business_certs(id) ON DELETE CASCADE,
    account_key TEXT,
    reason      TEXT NOT NULL,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_load_rejects_reason ON load_rejects(reason);
