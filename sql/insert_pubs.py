import overpy
import psycopg2
from shapely.geometry import Point

DB_CONFIG = {
    "dbname": "ukmap",
    "user": "postgres",
    "password": "thanatos",
    "host": "localhost"
}

def insert_pub(cursor, name, lat, lon):
    cursor.execute(
        """
        INSERT INTO pubs (name, lat, lon, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
        ON CONFLICT DO NOTHING;
        """,
        (name, lat, lon, lon, lat)
    )

def fetch_and_store_pubs():
    api = overpy.Overpass()
    print("Querying Overpass for pubs...")
    result = api.query("""
        area["name"="United Kingdom"]->.searchArea;
        node["amenity"="pub"](area.searchArea);
        out body;
    """)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print(f"Found {len(result.nodes)} pubs.")
    for node in result.nodes:
        name = node.tags.get("name", "Unnamed pub")
        insert_pub(cur, name, float(node.lat), float(node.lon))

    conn.commit()
    cur.close()
    conn.close()
    print("Finished inserting pubs.")

if __name__ == "__main__":
    fetch_and_store_pubs()

