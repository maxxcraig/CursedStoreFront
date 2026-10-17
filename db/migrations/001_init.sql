--starter schema for the skeleton. Thea's schema issue
-- extends this (exclusion constraint, categories table, views).

CREATE TABLE addresses (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    street      TEXT NOT NULL,
    unit        TEXT,
    city        TEXT NOT NULL DEFAULT 'San Diego',
    zip         TEXT
);

CREATE TABLE businesses (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT
);

CREATE TABLE occupancies (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    address_id  INTEGER NOT NULL REFERENCES addresses(id),
    business_id INTEGER NOT NULL REFERENCES businesses(id),
    opened_on   DATE NOT NULL,
    closed_on   DATE   --NULL means the business is still open
);