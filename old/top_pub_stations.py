import psycopg2
import csv
from config import PASSWORD

# DB config
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
  nr.name AS nearest_river,
  COUNT(p.*) AS nearby_pub_count
FROM (
  SELECT DISTINCT s.*
  FROM train_stations s
  JOIN rivers r ON ST_DWithin(s.geom, r.geom, 2000)
  WHERE s.lat < 52.2053
    AND s.lon < -0.6039067
) s
JOIN LATERAL (
  SELECT r.name
  FROM rivers r
  WHERE r.name IS NOT NULL
  ORDER BY s.geom <-> r.geom
  LIMIT 1
) nr ON TRUE
LEFT JOIN pubs p ON ST_DWithin(p.geom, s.geom, 5000)
GROUP BY s.name, s.lat, s.lon, nr.name
ORDER BY nearby_pub_count DESC;
"""

with conn.cursor() as cur:
    cur.execute(query)
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    with open("top_pub_stations.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

conn.close()
print("Exported top 20 pub-heavy stations to top_pub_stations.csv")

