# Performance check (issue 14)

Timings for the queries the app runs most, before and after the indexes in
`db/migrations/006_indexes.sql`. This is the baseline for the Phase 2
experiments.

## Setup

- Postgres 16 in Docker, default settings, on a laptop.
- Fresh database: `python -m db.migrate --seed`, then
  `python db/tests/perf_fake_data.py 200000`. That gives 200,006 addresses,
  550,881 businesses and 550,881 occupancies, about the size of the real city
  dataset (633,317 certificates).
- Queries are in `db/tests/perf_queries.sql`. Each was run with
  `EXPLAIN (ANALYZE, BUFFERS)` twice and the second (warm cache) time is
  reported.

## Results

| Query | Before | After | What changed |
|---|---:|---:|---|
| Address page history (`WHERE address_id = ? ORDER BY opened_on`) | 0.33 ms | 0.05 ms | Index scan on `(address_id, opened_on)`, no sort step |
| Curse view top 25 (leaderboard) | 379 ms | 241 ms | Merge join through the same index instead of a hash join over a full scan |
| Search as currently written (`street ILIKE ... OR b.name ILIKE ...`) | 191 ms | 73 ms | Plan unchanged, trigram indexes not used (see below) |
| Search rewritten as a UNION | 67 ms | 8 ms | Both trigram indexes used |
| Home page (every address with counts) | 460 ms | 455 ms | No change |

## Why each index helps

**`idx_occupancies_address_opened` on `occupancies (address_id, opened_on)`.**
The address page asks for one address's rows in date order. The exclusion
constraint from 003 already has a GiST index that can find the rows, but it
returns them unsorted, so Postgres added a sort. A btree on both columns
hands the rows back already in order. The curse view also joins occupancies
to addresses by `address_id`, and the planner now walks this index in
address order and merge-joins, which is cheaper than hashing all 550k rows.

**`idx_occupancies_business` on `occupancies (business_id)`.** Postgres does
not index foreign keys on its own. This covers the join from businesses back
to occupancies, used by the business half of search and by any future
"where has this business been" page.

**`idx_addresses_street_trgm` and `idx_businesses_name_trgm` (pg_trgm GIN).**
The search page uses `ILIKE '%text%'`. A normal btree can't help when the
pattern starts with a wildcard. pg_trgm indexes every three-letter chunk of
each value, so a substring search becomes an index lookup.

## What the indexes don't fix

**The search query as written can't use the trigram indexes.** It ORs a
condition on `addresses.street` with a condition on `businesses.name` across
a LEFT JOIN. Postgres has to look at every address to evaluate that OR, so
it ignores both indexes. Splitting it into two queries joined with UNION
(street matches, then business name matches) lets each half use its index,
and goes from 67 ms to 8 ms. The search route in `app/routes.py` now does
this, and the leaderboard route reads from `curse_scores` instead of
repeating the math inline.

**The home page and the curse view are whole-table aggregates.** They count
and average every occupancy for every address, then sort. No index can skip
work there. The home page also spills its sort to disk (about 10 MB). The
Phase 2 options are to paginate the home page, or to turn `curse_scores`
into a materialized view refreshed after each data load, so the leaderboard
reads precomputed rows.

## Index sizes

| Index | Size |
|---|---:|
| idx_addresses_street_trgm | 11 MB |
| idx_businesses_name_trgm | 14 MB |
| idx_occupancies_address_opened | 12 MB |
| idx_occupancies_business | 12 MB |

Small next to the tables, and they only slow down inserts, which happen in
one batch when the city data is loaded.
