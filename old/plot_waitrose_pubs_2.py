import csv
import folium

csv_file = "csv/waitrose_pubs_2.csv"
output_html = "html/waitrose_pubs_map_2.html"

# Create map centered on UK
m = folium.Map(location=[54.0, -2.0], zoom_start=6)

# Read CSV and add markers
with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pub_lat = float(row["pub_lat"])
        pub_lon = float(row["pub_lon"])
        waitrose_name = row["waitrose_name"]
        pub_name = row["pub_name"]

        label = f"<b>{waitrose_name}</b><br>{pub_name}"

        folium.Marker(
            location=[pub_lat, pub_lon],
            popup=folium.Popup(label, max_width=300),
            icon=folium.Icon(color="green", icon="shopping-cart", prefix="fa")
        ).add_to(m)

# Save map
m.save(output_html)
print(f"✅ Map saved to {output_html}")

