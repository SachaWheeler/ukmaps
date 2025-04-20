import osmnx as ox
print(ox.__version__)
gdf = ox.geometries_from_place("London, UK", tags={"amenity": "pub"})
print(gdf.head())

