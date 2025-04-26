import folium
import pandas as pd

# --- Load CSV ---
csv_file = "csv/waitrose_pubs.csv"  # update this to your actual file
df = pd.read_csv(csv_file)

# --- Create Map Centered on the UK ---
uk_map = folium.Map(location=[54.0, -2.0], zoom_start=6)

# --- Add Pub Markers ---
for _, row in df.iterrows():
    name = row.get("pub_name") or row.get("name")  # handle case differences
    lat = row["pub_lat"]
    lon = row["pub_lon"]

    folium.CircleMarker(
        location=(lat, lon),
        radius=4,
        color="blue",
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(name, max_width=200)
    ).add_to(uk_map)

# --- Save Map ---
uk_map.save("uk_pubs_map.html")
print("✅ Map saved to uk_pubs_map.html")

