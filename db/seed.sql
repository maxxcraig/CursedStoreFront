--seed.sql
--fake starter data so pages show something before real city data is added
--I used AI to make up all addresses and businesses, tried to include all possible outcomes
--like lots of turnover, medium amount, low amount, two units same building, and vacant

INSERT INTO addresses (street, unit, zip) VALUES
    ('100 Seabreeze Ave', NULL, '92107'),
    ('215 Gull St',       NULL, '92107'),
    ('340 Driftwood Ln',  'A',  '92109'),
    ('340 Driftwood Ln',  'B',  '92109'),
    ('512 Kelp Way',      NULL, '92101'),
    ('77 Harbor View Dr', NULL, '92106');

INSERT INTO categories (name) VALUES
    ('Restaurant'),
    ('Bar'),
    ('Fitness'),
    ('Retail'),
    ('Healthcare'),
    ('Salon'),
    ('Entertainment');

--look up each category by name, same idea as the occupancies insert below
INSERT INTO businesses (name, category_id)
SELECT v.name, c.id
FROM (VALUES
    ('Sunset Poke',          'Restaurant'),
    ('Tidewater Tacos',      'Restaurant'),
    ('Brew & Barrel',        'Bar'),
    ('Pacific Smoothie Co',  'Restaurant'),
    ('Golden Hour Yoga',     'Fitness'),
    ('Salt Line Surf Shop',  'Retail'),
    ('Old Pier Hardware',    'Retail'),
    ('Marina Dental',        'Healthcare'),
    ('Coastline Cuts',       'Salon'),
    ('Night Owl Arcade',     'Entertainment'),
    ('Breakwater Books',     'Retail')
) AS v(name, category)
JOIN categories c ON c.name = v.category;

--link businesses to addresses by name, so we don't depend on ID numbers
INSERT INTO occupancies (address_id, business_id, opened_on, closed_on)
SELECT a.id, b.id, v.opened_on::date, v.closed_on::date
FROM (VALUES
    --the cursed example, five businesses in under nine years
    ('100 Seabreeze Ave', NULL, 'Sunset Poke',         '2017-03-01', '2018-05-31'),
    ('100 Seabreeze Ave', NULL, 'Tidewater Tacos',     '2018-09-01', '2019-12-31'),
    ('100 Seabreeze Ave', NULL, 'Brew & Barrel',       '2020-04-01', '2021-02-28'),
    ('100 Seabreeze Ave', NULL, 'Pacific Smoothie Co', '2021-07-01', '2023-01-31'),
    ('100 Seabreeze Ave', NULL, 'Night Owl Arcade',    '2023-06-01', NULL),
    --stable one, same business since 1998
    ('215 Gull St',       NULL, 'Old Pier Hardware',   '1998-05-01', NULL),
    --two units at the same building
    ('340 Driftwood Ln',  'A',  'Golden Hour Yoga',    '2019-01-15', '2020-03-31'),
    ('340 Driftwood Ln',  'A',  'Coastline Cuts',      '2021-02-01', NULL),
    ('340 Driftwood Ln',  'B',  'Salt Line Surf Shop', '2012-06-01', NULL),
    --moderate turnover
    ('512 Kelp Way',      NULL, 'Breakwater Books',    '2009-10-01', '2016-08-31'),
    ('512 Kelp Way',      NULL, 'Marina Dental',       '2016-12-01', NULL)
    -- 77 Harbor View Dr left empty on purpose: a vacant address
) AS v(street, unit, business, opened_on, closed_on)
JOIN addresses  a ON a.street = v.street
                 AND a.unit IS NOT DISTINCT FROM v.unit
JOIN businesses b ON b.name = v.business;