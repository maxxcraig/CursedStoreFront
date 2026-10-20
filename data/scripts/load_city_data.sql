DELETE FROM occupancies
WHERE source = 'city';

INSERT INTO categories (name)
SELECT DISTINCT COALESCE(
    NULLIF(BTRIM(naics_description), ''),
    NULLIF(BTRIM(naics_sector), ''),
    'Unknown'
)
FROM city_business_staging
ON CONFLICT DO NOTHING;

INSERT INTO addresses (street, unit, city, zip, lat, lng)
SELECT DISTINCT
    BTRIM(CONCAT_WS(
        ' ',
        NULLIF(BTRIM(address_no), ''),
        NULLIF(BTRIM(address_pd), ''),
        NULLIF(BTRIM(address_road), ''),
        NULLIF(BTRIM(address_sfx), '')
    )),
    NULLIF(BTRIM(address_suite), ''),
    COALESCE(NULLIF(BTRIM(address_city), ''), 'San Diego'),
    NULLIF(BTRIM(address_zip), ''),
    CASE WHEN pg_input_is_valid(lat, 'numeric') THEN lat::numeric END,
    CASE WHEN pg_input_is_valid(lng, 'numeric') THEN lng::numeric END
FROM city_business_staging
WHERE NULLIF(BTRIM(address_no), '') IS NOT NULL
  AND NULLIF(BTRIM(address_road), '') IS NOT NULL
ON CONFLICT DO NOTHING;

INSERT INTO businesses (
    name,
    category_id,
    account_key,
    owner_name,
    ownership_type,
    naics_code
)
SELECT DISTINCT ON (s.account_key)
    COALESCE(NULLIF(BTRIM(s.dba_name), ''), NULLIF(BTRIM(s.business_owner_name), '')),
    c.id,
    BTRIM(s.account_key),
    NULLIF(BTRIM(s.business_owner_name), ''),
    NULLIF(BTRIM(s.ownership_type), ''),
    NULLIF(BTRIM(s.naics_code), '')
FROM city_business_staging s
JOIN categories c
  ON c.name = COALESCE(
        NULLIF(BTRIM(s.naics_description), ''),
        NULLIF(BTRIM(s.naics_sector), ''),
        'Unknown'
     )
WHERE NULLIF(BTRIM(s.account_key), '') IS NOT NULL
ORDER BY s.account_key
ON CONFLICT (account_key) DO NOTHING;

CREATE TEMP TABLE city_candidates AS
SELECT
    s.account_key,
    a.id AS address_id,
    b.id AS business_id,
    CASE
        WHEN pg_input_is_valid(s.date_cert_effective, 'timestamp')
        THEN s.date_cert_effective::timestamp::date
    END AS opened_on,
    CASE
        WHEN s.account_status = 'Cancelled'
         AND pg_input_is_valid(s.date_cert_expiration, 'timestamp')
        THEN s.date_cert_expiration::timestamp::date
    END AS closed_on,
    to_jsonb(s) AS raw_row
FROM city_business_staging s
JOIN businesses b
  ON b.account_key = BTRIM(s.account_key)
JOIN addresses a
  ON a.street = BTRIM(CONCAT_WS(
        ' ',
        NULLIF(BTRIM(s.address_no), ''),
        NULLIF(BTRIM(s.address_pd), ''),
        NULLIF(BTRIM(s.address_road), ''),
        NULLIF(BTRIM(s.address_sfx), '')
     ))
 AND a.unit IS NOT DISTINCT FROM NULLIF(BTRIM(s.address_suite), '')
 AND a.zip IS NOT DISTINCT FROM NULLIF(BTRIM(s.address_zip), '');

INSERT INTO load_rejects (account_key, reason, raw_row)
SELECT account_key, 'invalid dates', raw_row
FROM city_candidates
WHERE opened_on IS NULL
   OR (closed_on IS NOT NULL AND closed_on < opened_on);

DELETE FROM city_candidates
WHERE opened_on IS NULL
   OR (closed_on IS NOT NULL AND closed_on < opened_on);

INSERT INTO load_rejects (account_key, reason, raw_row)
SELECT DISTINCT c1.account_key, 'overlapping occupancy', c1.raw_row
FROM city_candidates c1
JOIN city_candidates c2
  ON c1.address_id = c2.address_id
 AND c1.account_key <> c2.account_key
 AND daterange(c1.opened_on, c1.closed_on, '[]')
     &&
     daterange(c2.opened_on, c2.closed_on, '[]');

DELETE FROM city_candidates c
WHERE EXISTS (
    SELECT 1
    FROM city_candidates other
    WHERE other.address_id = c.address_id
      AND other.account_key <> c.account_key
      AND daterange(c.opened_on, c.closed_on, '[]')
          &&
          daterange(other.opened_on, other.closed_on, '[]')
);

INSERT INTO occupancies (
    address_id,
    business_id,
    opened_on,
    closed_on,
    source
)
SELECT address_id, business_id, opened_on, closed_on, 'city'
FROM city_candidates;