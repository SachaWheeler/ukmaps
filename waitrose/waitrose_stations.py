import folium
import psycopg2
from config import PASSWORD

# --- DB connection ---
conn = psycopg2.connect(
    dbname="ukmap",
    user="postgres",
    password=PASSWORD,
    host="localhost"
)

cur = conn.cursor()

# --- Bounding Box conditions ---
lat_max = 52.2053
lon_max = -0.1

# --- Query Waitrose locations (bounded) ---
cur.execute("""
    SELECT id, name, lat, lon, geom
    FROM waitrose
    WHERE lat < %s AND lon < %s
      AND lat IS NOT NULL AND lon IS NOT NULL;
""", (lat_max, lon_max))
waitrose_data = cur.fetchall()

# Save Waitrose IDs to match
waitrose_ids = [row[0] for row in waitrose_data]

# --- Query Train Stations within 4 km of any Waitrose ---
# Using a spatial JOIN
cur.execute("""
    SELECT DISTINCT s.name, s.lat, s.lon
    FROM train_stations s
    JOIN waitrose w ON ST_DWithin(s.geom, w.geom, 4000)
    WHERE w.lat < %s AND w.lon < %s
      AND s.lat IS NOT NULL AND s.lon IS NOT NULL
      AND w.lat IS NOT NULL AND w.lon IS NOT NULL;
""", (lat_max, lon_max))
station_data = cur.fetchall()

cur.close()
conn.close()

# --- Create map centered roughly ---
m = folium.Map(location=[51.5, -1.5], zoom_start=8)

# --- Plot Waitrose stores (Green) ---
for _, name, lat, lon, _ in waitrose_data:
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(name, max_width=250),
        icon=folium.Icon(color="green", icon="shopping-cart", prefix="fa")
    ).add_to(m)

# --- Plot Train stations within 4km (Red) ---
for name, lat, lon in station_data:
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(name, max_width=250),
        icon=folium.Icon(color="red", icon="train", prefix="fa")
    ).add_to(m)

# --- Save map ---
m.save("waitrose_and_nearby_stations_map.html")
print("✅ Map saved to waitrose_and_nearby_stations_map.html")

