import folium
import psycopg2
from config import PASSWORD


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
lon_max = 1.5

# London
london_lat_min, london_lat_max = 51.28, 51.70  # lat_min, lat_max for London
london_lon_min, london_lon_max = -0.53, 0.30  # lon_min, lon_max for London

WAITROSE_STATION_DISTANCE = 2000
WAITROSE_PUB_DISTANCE = 3000

# Query towns with proximity and bounding box filters
cur.execute(
    """
    SELECT t.name, t.lat, t.lon
    FROM towns t
    WHERE t.lat <= %s AND t.lon <= %s
      AND NOT (t.lat BETWEEN %s AND %s AND t.lon BETWEEN %s AND %s)
      AND EXISTS (
          SELECT 1 FROM train_stations ts
          WHERE ST_DWithin(t.geom, ts.geom, 1000)
      )
      AND EXISTS (
          SELECT 1 FROM waitrose w
          WHERE ST_DWithin(t.geom, w.geom, 1000)
      )
""",
    (lat_max, lon_max, london_lat_min, london_lat_max, london_lon_min, london_lon_max),
)


results = cur.fetchall()

# --- Query railway lines ---
cur.execute(
    """
    SELECT ST_AsGeoJSON(way)
    FROM planet_osm_line
    WHERE railway = 'rail'
      AND ST_Y(ST_Centroid(way)) < %s
      AND ST_X(ST_Centroid(way)) < %s
      AND NOT (
          ST_Y(ST_Centroid(way)) BETWEEN %s AND %s AND
          ST_X(ST_Centroid(way)) BETWEEN %s AND %s
      );
    """,
    (lat_max, lon_max, london_lat_min, london_lat_max, london_lon_min, london_lon_max),
)

railway_geoms = cur.fetchall()

# --- Query AONB (Area of Outstanding Natural Beauty) geometries ---
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


# CSV of personal points
points_df = pd.read_csv("points.csv")

# Initialize Folium map
m = folium.Map(location=[51, -2.5], zoom_start=9)

# Add each qualifying town to the map
for name, lat, lon in results:
     folium.Marker(
             location=[station_lat, station_lon],
             popup=folium.Popup(f"{name}", parse_html=True),
             icon=folium.Icon(color="red", icon="train", prefix="fa"),
             ).add_to(m)
     """
     folium.CircleMarker(
         location=[lat, lon],
         radius=5,
         popup=folium.Popup(f"<b>{name}</b>", parse_html=True),
         color="blue",
         fill=True,
         fill_opacity=0.6,
     ).add_to(m)
     """


# Save to HTML
m.save("towns_with_station_and_waitrose.html")

# Clean up
cur.close()
conn.close()
