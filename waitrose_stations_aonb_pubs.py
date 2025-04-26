import folium
from folium import GeoJson
import psycopg2
import json
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
lat_max = 52
lon_max = -0.5

# --- Query Waitrose locations (bounded) ---
cur.execute("""
    SELECT id, name, lat, lon, geom
    FROM waitrose
    WHERE lat < %s AND lon < %s
      AND lat IS NOT NULL AND lon IS NOT NULL;
""", (lat_max, lon_max))
waitrose_data = cur.fetchall()

# --- Query Train Stations within 4 km of any Waitrose ---
cur.execute("""
    SELECT DISTINCT s.name, s.lat, s.lon
    FROM train_stations s
    JOIN waitrose w ON ST_DWithin(s.geom, w.geom, 4000)
    WHERE w.lat < %s AND w.lon < %s
      AND s.lat IS NOT NULL AND s.lon IS NOT NULL
      AND w.lat IS NOT NULL AND w.lon IS NOT NULL;
""", (lat_max, lon_max))
station_data = cur.fetchall()

# --- Query AONB geometries ---
cur.execute("""
    SELECT ST_AsGeoJSON(geom)
    FROM aonbs
    WHERE ST_Y(ST_Centroid(geom)) < %s
      AND ST_X(ST_Centroid(geom)) < %s
      AND geom IS NOT NULL;
""", (lat_max, lon_max))
aonb_geoms = cur.fetchall()

# --- Create map centered roughly ---
m = folium.Map(location=[51, -2.5], zoom_start=9)

# --- For each Waitrose, find 5 closest pubs within 3 km ---
for waitrose_id, waitrose_name, lat, lon, geom in waitrose_data:
    # Query pubs for this Waitrose
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT p.name, ST_Distance(w.geom, p.geom) AS dist_m
        FROM pubs p
        JOIN waitrose w ON w.id = %s
        WHERE ST_DWithin(p.geom, w.geom, 3000)
        ORDER BY dist_m ASC
        LIMIT 5;
    """, (waitrose_id,))
    pubs_nearby = cur.fetchall()
    cur.close()

    # Create popup text
    popup_html = f"<b>{waitrose_name}</b><br><br><u>Nearby pubs within 3 km:</u><br>"
    if pubs_nearby:
        for pub_name, dist_m in pubs_nearby:
            popup_html += f"- {pub_name} ({round(dist_m)} m)<br>"
    else:
        popup_html += "(No pubs found within 3 km)"

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="green", icon="shopping-cart", prefix="fa")
    ).add_to(m)

# --- Plot Train stations within 4km (Red) ---
for name, lat, lon in station_data:
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(name, max_width=250),
        icon=folium.Icon(color="red", icon="train", prefix="fa")
    ).add_to(m)

# --- Add AONB outlines as GeoJSON ---
for geom_json, in aonb_geoms:
    if geom_json:
        geojson = json.loads(geom_json)
        folium.GeoJson(
            geojson,
            style_function=lambda feature: {
                'fillOpacity': 0,
                'color': 'blue',
                'weight': 2
            }
        ).add_to(m)

conn.close()

# --- Save map ---
m.save("waitrose_stations_aonb_pubs_map.html")
print("✅ Map saved to waitrose_stations_aonb_pubs_map.html")

