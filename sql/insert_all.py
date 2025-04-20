import overpy
import psycopg2
from shapely.geometry import LineString
from time import sleep

DB_CONFIG = {
    "dbname": "ukmap",
    "user": "postgres",
    "password": "thanatos",
    "host": "localhost"
}

def connect_db():
    return psycopg2.connect(**DB_CONFIG)

def insert_point_feature(cur, table, name, lat, lon):
    cur.execute(
        f"""
        INSERT INTO {table} (name, lat, lon, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
        ON CONFLICT DO NOTHING
        """,
        (name, lat, lon, lon, lat)
    )

def insert_linestring_feature(cur, table, name, coords):
    if len(coords) < 2:
        return  # not a valid linestring
    wkt = LineString(coords).wkt
    cur.execute(
        f"""
        INSERT INTO {table} (name, geom)
        VALUES (%s, ST_GeogFromText(%s))
        ON CONFLICT DO NOTHING
        """,
        (name, wkt)
    )

def fetch_nodes(query):
    api = overpy.Overpass()
    result = api.query(query)
    return result.nodes

def fetch_ways(query):
    api = overpy.Overpass()
    result = api.query(query)
    return result.ways

def load_pubs(conn):
    print("Loading pubs...")
    query = """
    area["name"="United Kingdom"]->.searchArea;
    node["amenity"="pub"](area.searchArea);
    out body;
    """
    nodes = fetch_nodes(query)
    with conn.cursor() as cur:
        for node in nodes:
            name = node.tags.get("name", "Unnamed pub")
            insert_point_feature(cur, "pubs", name, float(node.lat), float(node.lon))
    conn.commit()
    print(f"Inserted {len(nodes)} pubs.")

def load_towns(conn):
    print("Loading towns...")
    query = """
    area["name"="United Kingdom"]->.searchArea;
    node["place"="town"](area.searchArea);
    out body;
    """
    nodes = fetch_nodes(query)
    with conn.cursor() as cur:
        for node in nodes:
            name = node.tags.get("name", "Unnamed town")
            insert_point_feature(cur, "towns", name, float(node.lat), float(node.lon))
    conn.commit()
    print(f"Inserted {len(nodes)} towns.")

def load_train_stations(conn):
    print("Loading train stations...")
    query = """
    area["name"="United Kingdom"]->.searchArea;
    node["railway"="station"](area.searchArea);
    out body;
    """
    nodes = fetch_nodes(query)
    with conn.cursor() as cur:
        for node in nodes:
            name = node.tags.get("name", "Unnamed station")
            insert_point_feature(cur, "train_stations", name, float(node.lat), float(node.lon))
    conn.commit()
    print(f"Inserted {len(nodes)} stations.")

def load_rivers(conn):
    print("Loading rivers...")
    query = """
    area["name"="United Kingdom"]->.searchArea;
    way["waterway"="river"](area.searchArea);
    out body;
    >;
    out skel qt;
    """
    ways = fetch_ways(query)
    print(f"Fetched {len(ways)} rivers")
    with conn.cursor() as cur:
        for way in ways:
            try:
                coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
                name = way.tags.get("name", "Unnamed river")
                insert_linestring_feature(cur, "rivers", name, coords)
            except Exception as e:
                print(f"Error processing river: {e}")
    conn.commit()
    print(f"Inserted {len(ways)} rivers.")

def main():
    conn = connect_db()
    try:
        load_towns(conn)
        sleep(10)
        load_pubs(conn)
        sleep(10)
        load_train_stations(conn)
        sleep(10)
        load_rivers(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()

