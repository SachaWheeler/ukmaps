import json
import psycopg2

# --- Config ---
json_file = "Waitrose_Store_Locations_Data.json"

conn = psycopg2.connect(
    dbname="ukmap",
    user="postgres",
    password="thanatos",
    host="localhost"
)
cur = conn.cursor()

# --- Create table if needed ---
cur.execute("""
CREATE TABLE IF NOT EXISTS Waitrose (
    id SERIAL PRIMARY KEY,
    name TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    geom GEOGRAPHY(POINT, 4326)
)
""")

# --- Load JSON ---
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])

# --- Insert each feature ---
for f in features:
    props = f["properties"]
    name = props.get("Name")
    lat = float(props.get("Latitude"))
    lon = float(props.get("Longitude"))

    cur.execute("""
        INSERT INTO Waitrose (name, lat, lon, geom)
        VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)
    """, (name, lat, lon, lon, lat))

conn.commit()
cur.close()
conn.close()

print(f"✅ Inserted {len(features)} stores into the Waitrose table.")

