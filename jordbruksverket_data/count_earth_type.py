import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import json

# Load your JSON file (coordinates assumed to be in SWEREF, EPSG:3006)
with open("jordbruksverket_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# Convert the list of records into a DataFrame
df_points = pd.DataFrame(data)

# Create a geometry column from 'longitud' and 'latitud'
df_points["geometry"] = df_points.apply(lambda row: Point(row["longitud"], row["latitud"]), axis=1)

# Convert to a GeoDataFrame with the appropriate CRS
points_gdf = gpd.GeoDataFrame(df_points, geometry="geometry", crs="EPSG:3006")

# Apply a buffer (e.g., 10 meters) to each point to account for boundary issues
points_gdf["geometry"] = points_gdf.geometry.buffer(10)

# Load the soil dataset (assuming the layer name is 'grundlager')
soil_gdf = gpd.read_file("C:/Users/joso0/Downloads/jordarter25k_100k.gpkg", layer='grundlager')

# Perform a spatial join: match each buffered point with intersecting soil polygons
# (geopandas 0.10+ uses "predicate" instead of "op")
joined = gpd.sjoin(points_gdf, soil_gdf, how="left", predicate="intersects")

# Iterate over the joined GeoDataFrame and update the original JSON records
# "jg2_tx" is assumed to be the soil type column in the soil dataset.
# If no match is found, we assign None.
for idx, row in joined.iterrows():
    soil_type = row.get("jg2_tx")
    data[idx]["jordart_sgu"] = soil_type if pd.notnull(soil_type) else None

# Dump the updated JSON data to a new file
with open("updated_jordbruksverket_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)



