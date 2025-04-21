WITH waitrose_candidates AS (
  SELECT *
  FROM waitrose
  WHERE lat < 52.3053 AND lon < -0.6039
),
waitrose_near_river_station AS (
  SELECT w.*
  FROM waitrose_candidates w
  JOIN rivers r ON ST_DWithin(w.geom, r.geom, 5000)
  JOIN train_stations s ON ST_DWithin(w.geom, s.geom, 5000)
),
waitrose_with_nearest_river AS (
  SELECT
    w.*,
    r.name AS nearest_river
  FROM waitrose_near_river_station w
  JOIN LATERAL (
    SELECT r.name
    FROM rivers r
    WHERE r.name IS NOT NULL
    ORDER BY w.geom <-> r.geom
    LIMIT 1
  ) r ON TRUE
),
waitrose_pub_count AS (
  SELECT
    w.name AS waitrose_name,
    COUNT(DISTINCT p.id) AS pub_count
  FROM waitrose_near_river_station w
  JOIN pubs p ON ST_DWithin(p.geom, w.geom, 5000)
  GROUP BY w.name
),
waitrose_with_top_pubs AS (
  SELECT
    w.name AS waitrose_name,
    w.nearest_river,
    p.name AS pub_name,
    p.lat AS pub_lat,
    p.lon AS pub_lon,
    ST_Distance(w.geom, p.geom) AS distance_to_pub_m
  FROM waitrose_with_nearest_river w
  JOIN LATERAL (
    SELECT p.*
    FROM pubs p
    WHERE ST_DWithin(p.geom, w.geom, 5000)
    ORDER BY w.geom <-> p.geom
    LIMIT 5
  ) p ON TRUE
)
SELECT
  w.waitrose_name,
  w.nearest_river,
  w.pub_name,
  w.pub_lat,
  w.pub_lon,
  ROUND(w.distance_to_pub_m::numeric, 1) AS distance_to_pub_m,
  c.pub_count
FROM waitrose_with_top_pubs w
JOIN waitrose_pub_count c ON w.waitrose_name = c.waitrose_name
ORDER BY w.waitrose_name, w.distance_to_pub_m;

