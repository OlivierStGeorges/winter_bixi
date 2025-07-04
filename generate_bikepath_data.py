import geopandas as gpd

# 1. Charger les données
hexagones = gpd.read_file("hexagone/GenerateTessellation_nouveaushp.shp")  # grille de tessellation
reseau = gpd.read_file("data/piste_cyclable/reseau_cyclable_protégé.shp")  # lignes cyclables

# 2. Reprojeter en mètres (EPSG:32188 = NAD83 / MTM zone 8)
hexagones = hexagones.to_crs(epsg=32188)
reseau = reseau.to_crs(epsg=32188)

# 3. S'assurer que l'index est bien défini
hexagones = hexagones.reset_index().rename(columns={"index": "hex_index"})

# 4. Intersection spatiale (lignes découpées par polygones)
inter = gpd.overlay(reseau, hexagones, how="intersection")

# 5. Recalculer la longueur des segments dans chaque hexagone
inter["longueur_m"] = inter.geometry.length

# 6. Agréger par 'hex_index'
grouped = inter.groupby("hex_index")["longueur_m"].sum().reset_index()
grouped["longueur_km"] = grouped["longueur_m"] / 1000

# 7. Fusionner les longueurs dans la grille d'origine
hexagones = hexagones.merge(grouped, on="hex_index", how="left")
hexagones["longueur_km"] = hexagones["longueur_km"].fillna(0)

# 8. Exporter le résultat
hexagones.to_file("hexagones_avec_longueur_protégé.shp")


