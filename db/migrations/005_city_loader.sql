CREATE TABLE city_business_staging (
    account_key TEXT,
    account_status TEXT,
    date_account_creation TEXT,
    date_cert_expiration TEXT,
    date_cert_effective TEXT,
    business_owner_name TEXT,
    ownership_type TEXT,
    date_business_start TEXT,
    dba_name TEXT,
    naics_sector TEXT,
    naics_code TEXT,
    naics_description TEXT,
    address_no TEXT,
    address_pd TEXT,
    address_road TEXT,
    address_sfx TEXT,
    address_no_fraction TEXT,
    address_city TEXT,
    address_state TEXT,
    address_zip TEXT,
    address_suite TEXT,
    address_pmb_box TEXT,
    address_po_box TEXT,
    bid TEXT,
    council_district TEXT,
    lat TEXT,
    lng TEXT
);

CREATE TABLE load_rejects (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_key TEXT,
    reason TEXT NOT NULL,
    raw_row JSONB NOT NULL,
    rejected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);