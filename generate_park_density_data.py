import geopandas as gpd
import pandas as pd

# 1. Charger les fichiers
gdf_hex = gpd.read_file("hexagone/GenerateTessellation_nouveaushp.shp")
gdf_parc = gpd.read_file("data/export(1)/export(1)-POLYGON.shp")

# Reprojection en MTM 8 (EPSG:32188)
gdf_hex = gdf_hex.to_crs("EPSG:32188")
gdf_parc = gdf_parc.to_crs("EPSG:32188")



gdf_hex["hex_id"] = gdf_hex.index.astype(str)

#print(gdf_hex.columns)
#print(gdf_ad.columns)


# 4. Calculer l’aire des aires des parcs
gdf_parc["aire_parc"] = gdf_parc.geometry.area  # en m²

# 5. Intersecter les hexagones avec les aires
inter = gpd.overlay(gdf_hex, gdf_parc, how="intersection")

# 6. Calculer l’aire de chaque polygone d’intersection
inter["aire_inter"] = inter.geometry.area

# 7. Calculer la population à transférer à chaque intersection
#inter["pop_inter"] = inter["population"] * (inter["aire_inter"] / inter["aire_ad"])

print("inter")
print(inter["aire_inter"].describe())

# 8. Agréger la population par hexagone
aire_par_hex = inter.groupby("hex_id").agg({"aire_inter": "sum"}).reset_index()
#print(gdf_hex.columns)
#print(gdf_hex["GRID_ID"].head(10))
#print(pop_par_hex["GRID_ID"].head(10))


#print(pop_par_hex.columns)
# 9. Fusionner avec la grille
gdf_hex = gdf_hex.merge(aire_par_hex, on="hex_id", how="left")
gdf_hex["aire_parc"] = gdf_hex["aire_inter"].fillna(0)

#print("gdf_hex")
#print(gdf_hex["pop_inter"].describe())

# 10. Calculer la densité dans chaque hexagone
#gdf_hex["aire_hex"] = gdf_hex.geometry.area  # en m²
#gdf_hex["densite_estimee"] = gdf_hex["pop_inter"] / gdf_hex["aire_hex"] * 1e6  # en hab/km²

print(gdf_hex['aire_parc'].describe())
print(gdf_hex.columns)
gdf_hex.to_file("hexagones_avec_parc.shp")