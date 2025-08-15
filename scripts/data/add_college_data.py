import geopandas as gpd

def ajouter_nombre_cegep_par_hexagone(path_hexagones, path_cegep, output_path):

    # 1. Charger les données
    hexagones = gpd.read_file(path_hexagones)
    cegeps = gpd.read_file(path_cegep)

    # 2. Harmoniser les systèmes de coordonnées
    hexagones = hexagones.to_crs(epsg=32188)
    cegeps = cegeps.to_crs(epsg=32188)

    # 4. Jointure spatiale
    cegeps_dans_hex = gpd.sjoin(cegeps, hexagones, how="left", predicate='within')

    # 5. Comptage par hexagone
    counts = cegeps_dans_hex.groupby("hex_index").size().reset_index(name="nb_cegep")

    # 6. Fusion dans la grille
    hexagones = hexagones.merge(counts, on="hex_index", how="left")
    hexagones["nb_cegep"] = hexagones["nb_cegep"].fillna(0).astype(int)

    # 7. Export
    hexagones.to_file(output_path)
