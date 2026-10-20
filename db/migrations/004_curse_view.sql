-- 004_curse_view.sql
-- Issue #13: the stats behind the "most cursed storefront" rankings.
--
-- curse_scores has one row per address:
--   occupancy_count     businesses ever on record at the address
--   avg_lifespan_days   average days from opened_on to closed_on, closed businesses only
--   closures_last_10y   businesses that closed in the last ten years
--   curse_score         see below
--
-- Formula:
--   curse_score = closures_last_10y * 365 / avg_lifespan_days
--
-- Read it as "closures in the last decade, times how many times a year a
-- typical tenant fails here". One closure with a one-year average lifespan
-- scores 1.0. Four closures averaging 15 months scores about 3.1. An address
-- with no closures, or none in the last ten years, scores 0.
--
-- The average lifespan is floored at 30 days so a single one-week pop-up
-- can't produce a huge score on its own.

CREATE VIEW curse_scores AS
WITH stats AS (
    SELECT
        a.id AS address_id,
        COUNT(o.id) AS occupancy_count,
        AVG(o.closed_on - o.opened_on) FILTER (WHERE o.closed_on IS NOT NULL)
            AS avg_lifespan_days,
        COUNT(o.id) FILTER (WHERE o.closed_on >= CURRENT_DATE - INTERVAL '10 years')
            AS closures_last_10y
    FROM addresses a
    LEFT JOIN occupancies o ON o.address_id = a.id
    GROUP BY a.id
)
SELECT
    a.id,
    a.street,
    a.unit,
    a.zip,
    s.occupancy_count,
    ROUND(s.avg_lifespan_days) AS avg_lifespan_days,
    s.closures_last_10y,
    ROUND(
        s.closures_last_10y * 365.0 / GREATEST(COALESCE(s.avg_lifespan_days, 365), 30),
        1
    ) AS curse_score
FROM addresses a
JOIN stats s ON s.address_id = a.id;
