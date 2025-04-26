import psycopg2
import csv
import argparse
from math import cos, radians
from config import PASSWORD

# --- Argument parser ---
parser = argparse.ArgumentParser(description="Export station-pub-river info within a bounding box.")
parser.add_argument("--lat", type=float, default=51.5, help="Center latitude (default: 51.5)")
parser.add_argument("--lon", type=float, default=-0.1, help="Center longitude (default: -0.1)")
parser.add_argument("--size", type=float, default=20, help="Bounding box size in km (default: 20)")
parser.add_argument("--outfile", type=str, default="station_pubs_bbox.csv", help="Output CSV file")

args = parser.parse_args()

center_lat = args.lat
center_lon = args.lon
half_side_km = args.size / 2

# --- Bounding box calculation ---
lat_deg_per_km = 1 / 110.574
lon_deg_per_km = 1 / (111.320 * cos(radians(center_lat)))

lat_min = center_lat - half_side_km * lat_deg_per_km
lat_max = center_lat + half_side_km * lat_deg_per_km
lon_min = center_lon - half_side_km * lon_deg_per_km
lon_max = center_lon + half_side_km * lon_deg_per_km

# --- Database query ---
conn = psycopg2.connect(
    dbname="ukmap",
    user="postgres",
    password=PASSWORD,
    host="localhost"
)

query = f"""
SELECT
  s.name AS station_name,
  s.lat AS station_lat,
  s.lon AS station_lon,
  nr.name AS nearest_river,
  p.name AS pub_name,
  p.lat AS pub_lat,
  p.lon AS pub_lon,
  ST_Distance(s.geom, p.geom) AS distance_to_pub_m
FROM (
  SELECT DISTINCT s.*
  FROM train_stations s
  JOIN rivers r ON ST_DWithin(s.geom, r.geom, 2000)
  WHERE s.lat BETWEEN {lat_min} AND {lat_max}
    AND s.lon BETWEEN {lon_min} AND {lon_max}
) s
JOIN LATERAL (
  SELECT r.name
  FROM rivers r
  ORDER BY s.geom <-> r.geom
  LIMIT 1
) nr ON TRUE
JOIN LATERAL (
  SELECT p.*
  FROM pubs p
  WHERE ST_DWithin(p.geom, s.geom, 5000)
    AND p.lat BETWEEN {lat_min} AND {lat_max}
    AND p.lon BETWEEN {lon_min} AND {lon_max}
  ORDER BY s.geom <-> p.geom
  LIMIT 5
) p ON TRUE
ORDER BY s.name, distance_to_pub_m;
"""

with conn.cursor() as cur:
    cur.execute(query)
    rows = cur.fetchall()
    headers = [desc[0] for desc in cur.description]

    with open(args.outfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

conn.close()
print(f"Exported to {args.outfile}")

