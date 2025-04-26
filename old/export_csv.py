import psycopg2
import csv
from config import PASSWORD

conn = psycopg2.connect(
    dbname="ukmap",
    user="postgres",
    password=PASSWORD,
    host="localhost"
)

query = """
SELECT
  s.name AS station_name,
  s.lat AS station_lat,
  s.lon AS station_lon,
  p.name AS pub_name,
  p.lat AS pub_lat,
  p.lon AS pub_lon,
  ST_Distance(s.geom, p.geom) AS distance_m
FROM nearby_river_stations s
JOIN LATERAL (
  SELECT *
  FROM pubs
  ORDER BY s.geom <-> pubs.geom  -- KNN index
  LIMIT 5
) p ON TRUE
ORDER BY s.name, distance_m;
"""

with conn.cursor() as cur:
    cur.execute(query)
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    with open("station_pubs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

conn.close()

