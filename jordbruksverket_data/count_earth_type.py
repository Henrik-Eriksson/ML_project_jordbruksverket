import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import json

#Adds SGU soil type information to each record by performing a spatial join between buffered points and a soil layer, then saves the updated data to a new JSON file.

with open("jordbruksverket_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df_points = pd.DataFrame(data)
df_points["geometry"] = df_points.apply(lambda row: Point(row["longitud"], row["latitud"]), axis=1)
points_gdf = gpd.GeoDataFrame(df_points, geometry="geometry", crs="EPSG:3006")
points_gdf["geometry"] = points_gdf.geometry.buffer(10)
soil_gdf = gpd.read_file("C:/Users/joso0/Downloads/jordarter25k_100k.gpkg", layer='grundlager')
joined = gpd.sjoin(points_gdf, soil_gdf, how="left", predicate="intersects")

for idx, row in joined.iterrows():
    soil_type = row.get("jg2_tx")
    data[idx]["jordart_sgu"] = soil_type if pd.notnull(soil_type) else None

with open("updated_jordbruksverket_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)