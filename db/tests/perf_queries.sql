\echo === address history (address page) ===
EXPLAIN (ANALYZE, BUFFERS)
SELECT b.name, c.name AS category, o.opened_on, o.closed_on
FROM occupancies o
JOIN businesses b ON b.id = o.business_id
LEFT JOIN categories c ON c.id = b.category_id
WHERE o.address_id = 25000
ORDER BY o.opened_on;

\echo === curse view top 25 (leaderboard) ===
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM curse_scores ORDER BY curse_score DESC LIMIT 25;

\echo === search by street or business name ===
EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT a.id, a.street, a.unit, a.zip
FROM addresses a
LEFT JOIN occupancies o ON o.address_id = a.id
LEFT JOIN businesses  b ON b.id = o.business_id
WHERE a.street ILIKE '%ridge%' OR b.name ILIKE '%ridge%'
ORDER BY a.street, a.unit
LIMIT 50;

\echo === home page (all addresses with counts) ===
EXPLAIN (ANALYZE, BUFFERS)
SELECT a.id, a.street, a.unit, a.zip,
       COUNT(o.id) AS occupancy_count,
       MAX(b.name) FILTER (WHERE o.closed_on IS NULL) AS current_business
FROM addresses a
LEFT JOIN occupancies o ON o.address_id = a.id
LEFT JOIN businesses  b ON b.id = o.business_id
GROUP BY a.id
ORDER BY occupancy_count DESC, a.street;
