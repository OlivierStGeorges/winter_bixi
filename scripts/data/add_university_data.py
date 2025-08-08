import geopandas as gpd

def ajouter_nombre_universites_par_hexagone(path_hexagones, path_universites, output_path):

    # 1. Charger les données
    hexagones = gpd.read_file(path_hexagones)
    universites = gpd.read_file(path_universites)

    # 2. Harmoniser les systèmes de coordonnées
    hexagones = hexagones.to_crs(epsg=32188)
    universites = universites.to_crs(epsg=32188)

    # 3. Index clair
#    hexagones = hexagones.reset_index().rename(columns={"index": "hex_index"})

    # 4. Jointure spatiale
    universites_dans_hex = gpd.sjoin(universites, hexagones, how="left", predicate='within')

    # 5. Comptage par hexagone
    counts = universites_dans_hex.groupby("hex_index").size().reset_index(name="nombre_universites")

    # 6. Fusion dans la grille
    hexagones = hexagones.merge(counts, on="hex_index", how="left")
    hexagones["nombre_universites"] = hexagones["nombre_universites"].fillna(0).astype(int)

    # 7. Export
    hexagones.to_file(output_path)
