import osmnx as ox
import psycopg2
from shapely.geometry import Point

conn = psycopg2.connect(
    dbname="ukmap",
    user="postgres",
    password="thanatos",
    host="localhost"
)
cur = conn.cursor()

# Fetch all pubs in the UK
gdf = ox.geometries_from_place("United Kingdom", tags={"amenity": "pub"})

for idx, row in gdf.iterrows():
    if 'name' in row and row.geometry.geom_type == "Point":
        name = row['name']
        lon, lat = row.geometry.x, row.geometry.y
        cur.execute(
            "INSERT INTO pubs (name, lat, lon, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)",
            (name, lat, lon, lon, lat)
        )

conn.commit()
cur.close()
conn.close()

