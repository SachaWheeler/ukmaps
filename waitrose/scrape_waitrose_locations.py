import requests
import csv

url = "https://www.waitrose.com/api/store-finder/stores?limit=10000"

response = requests.get(url)
response.raise_for_status()

data = response.json()
stores = data.get("results", [])

with open("waitrose_postcodes.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Store Name", "Postcode", "Address", "Latitude", "Longitude"])

    for store in stores:
        name = store.get("storeDisplayName", "")
        postcode = store.get("postcode", "")
        address = store.get("address", "")
        lat = store.get("latitude", "")
        lon = store.get("longitude", "")
        writer.writerow([name, postcode, address, lat, lon])

print(f"✅ Scraped {len(stores)} Waitrose stores into waitrose_postcodes.csv")

