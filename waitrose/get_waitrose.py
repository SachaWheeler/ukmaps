import requests
import re
import csv

url = "http://www.kevinlaurence.net/googlemaps/waitrose.html"
response = requests.get(url)
html = response.text

# Regex to extract entries like: ["Waitrose, Abingdon", 51.671139, -1.285381, 1]
pattern = re.compile(r'\["([^"]+)",\s*([\d.]+),\s*([-.\d]+),\s*\d+\]')

locations = pattern.findall(html)

with open("waitrose_latlon.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Store Name", "Latitude", "Longitude"])
    for name, lat, lon in locations:
        writer.writerow([name, lat, lon])

print(f"✅ Extracted {len(locations)} stores to waitrose_latlon.csv")

