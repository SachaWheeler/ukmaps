import folium
import pandas as pd
import psycopg2
from math import radians, sin, cos, sqrt, atan2
import json
from config import PASSWORD


# --- Haversine Distance Formula ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def estimate_travel_time(lat_from, lon_from, lat_to, lon_to, speed_kmh=100):
    distance_km = haversine(lat_from, lon_from, lat_to, lon_to)
    travel_time_hours = distance_km / speed_kmh
    return round(travel_time_hours * 60)  # return in minutes


# --- London and Abergavenny Locations ---
london_lat, london_lon = 51.5074, -0.1278
abergavenny_lat, abergavenny_lon = 51.825359, -3.0400269

# --- DB connection ---
conn = psycopg2.connect(
    dbname="ukmap", user="postgres", password=PASSWORD, host="localhost"
)

cur = conn.cursor()

# --- Bounding Box conditions ---
lat_max = 52.2
lon_max = -0.5

# --- Query railway lines ---
cur.execute(
    """
    SELECT ST_AsGeoJSON(way)
    FROM planet_osm_line
    WHERE railway = 'rail'
      AND ST_Y(ST_Centroid(way)) < %s
      AND ST_X(ST_Centroid(way)) < %s;
""",
    (lat_max, lon_max),
)
railway_geoms = cur.fetchall()

# --- Query Waitrose locations (bounded) ---
cur.execute(
    """
    SELECT id, name, lat, lon, geom
    FROM waitrose
    WHERE lat < %s AND lon < %s
      AND lat IS NOT NULL AND lon IS NOT NULL;
""",
    (lat_max, lon_max),
)
waitrose_data = cur.fetchall()

# --- Query Train Stations within 4 km of any Waitrose ---
cur.execute(
    """
    SELECT DISTINCT s.name, s.lat, s.lon
    FROM train_stations s
    JOIN waitrose w ON ST_DWithin(s.geom, w.geom, 4000)
    WHERE w.lat < %s AND w.lon < %s
      AND s.lat IS NOT NULL AND s.lon IS NOT NULL
      AND w.lat IS NOT NULL AND w.lon IS NOT NULL;
""",
    (lat_max, lon_max),
)
station_data = cur.fetchall()

# --- Query AONB geometries ---
cur.execute(
    """
    SELECT ST_AsGeoJSON(geom)
    FROM aonbs
    WHERE ST_Y(ST_Centroid(geom)) < %s
      AND ST_X(ST_Centroid(geom)) < %s
      AND geom IS NOT NULL;
""",
    (lat_max, lon_max),
)
aonb_geoms = cur.fetchall()


# CSV of personla points
points_df = pd.read_csv("points.csv")


# --- Create map centered roughly ---
m = folium.Map(location=[51, -2.5], zoom_start=9)

# --- Plot Waitrose stores (Green) and include 5 closest pubs ---
for waitrose_id, waitrose_name, lat, lon, geom in waitrose_data:
    # Query 5 closest pubs within 3km for this Waitrose
    pub_cursor = conn.cursor()
    pub_cursor.execute(
        """
        SELECT DISTINCT p.name, ST_Distance(w.geom, p.geom) AS dist_m
        FROM pubs p
        JOIN waitrose w ON w.id = %s
        WHERE ST_DWithin(p.geom, w.geom, 3000)
        ORDER BY dist_m ASC
        LIMIT 5;
    """,
        (waitrose_id,),
    )
    pubs_nearby = pub_cursor.fetchall()
    pub_cursor.close()

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
        icon=folium.Icon(color="green", icon="shopping-cart", prefix="fa"),
    ).add_to(m)

# --- Plot Train stations with Travel Times in Popups (Red) ---
for station_name, station_lat, station_lon in station_data:
    time_from_london = estimate_travel_time(
        london_lat, london_lon, station_lat, station_lon
    )
    time_from_abergavenny = estimate_travel_time(
        abergavenny_lat, abergavenny_lon, station_lat, station_lon
    )

    popup_html = f"""
    <b>{station_name}</b><br><br>
    ⏱️ Travel time:<br>
    - From London: {time_from_london} mins<br>
    - From Abergavenny: {time_from_abergavenny} mins
    """

    folium.Marker(
        location=[station_lat, station_lon],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color="red", icon="train", prefix="fa"),
    ).add_to(m)

# --- Add Railway lines as GeoJSON ---
for (geom_json,) in railway_geoms:
    if geom_json:
        geojson = json.loads(geom_json)
        folium.GeoJson(
            geojson,
            style_function=lambda feature: {
                "color": "black",
                "weight": 2,
                "opacity": 0.7,
            },
        ).add_to(m)


# --- Add AONB outlines as GeoJSON ---
for (geom_json,) in aonb_geoms:
    if geom_json:
        geojson = json.loads(geom_json)
        folium.GeoJson(
            geojson,
            style_function=lambda feature: {
                "fillOpacity": 0,
                "color": "blue",
                "weight": 2,
            },
        ).add_to(m)

# Add points
for _, row in points_df.iterrows():
    print(row)
    folium.Marker(
        location=[row["lat"], row["lon"]],
        icon=folium.Icon(color="orange", icon="star", prefix="fa"),  # Goldish star
        popup=row["name"],
    ).add_to(m)

conn.close()

# --- Save map ---
m.save("waitrose_stations_aonb_pubs_map.html")
print("✅ Map saved to waitrose_stations_aonb_pubs_map.html")
