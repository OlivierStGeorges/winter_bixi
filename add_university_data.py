import geopandas as gpd

# 1. Charger les données
hexagones = gpd.read_file("hexagone/GenerateTessellation_nouveaushp.shp")  # grille de tessellation
universites = gpd.read_file("data/etablissements-meq-mes-esrishp/ES_Universitaire.shp")  # points des universités

# 2. Reprojeter en mètres (même CRS pour faire les opérations spatiales)
hexagones = hexagones.to_crs(epsg=32188)
universites = universites.to_crs(epsg=32188)

# 3. S'assurer que l'index est bien défini
hexagones = hexagones.reset_index().rename(columns={"index": "hex_index"})

# 4. Spatial join : attribuer à chaque université l'hexagone dans lequel elle se trouve
universites_dans_hex = gpd.sjoin(universites, hexagones, how="left", predicate='within')

# 5. Compter le nombre d'universités par hexagone
counts = universites_dans_hex.groupby("hex_index").size().reset_index(name="nombre_universites")

# 6. Fusionner le nombre dans la grille
hexagones = hexagones.merge(counts, on="hex_index", how="left")
hexagones["nombre_universites"] = hexagones["nombre_universites"].fillna(0).astype(int)


print(hexagones["nombre_universites"].sum())
print(universites.shape)
# 7. Exporter le résultat
hexagones.to_file("hexagones_avec_nombre_universites.shp")
