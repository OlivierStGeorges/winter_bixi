import geopandas as gpd

def ajouter_longueur_pistes_protegees_par_hexagone(
    path_hexagones,
    path_reseau,
    output_path,
    epsg=32188  # MTM zone 8
):
    """
    Calcule la longueur de pistes cyclables protégées par hexagone et exporte le fichier enrichi.

    Paramètres :
    - path_hexagones : chemin vers le fichier des hexagones (shapefile ou geojson)
    - path_reseau    : chemin vers le shapefile des pistes cyclables protégées
    - output_path    : chemin du fichier de sortie (shp ou geojson selon extension)
    - epsg           : code EPSG pour reprojection (par défaut : 32188)
    """

    # Charger les fichiers
    hexagones = gpd.read_file(path_hexagones)
    reseau = gpd.read_file(path_reseau)

    # Reprojection
    hexagones = hexagones.to_crs(epsg=epsg)
    reseau = reseau.to_crs(epsg=epsg)

    # Index propre
    hexagones = hexagones.reset_index().rename(columns={"index": "hex_index"})

    # Intersection spatiale
    inter = gpd.overlay(reseau, hexagones, how="intersection")

    # Longueur de segments
    inter["longueur_m"] = inter.geometry.length

    # Agrégation par hexagone
    grouped = inter.groupby("hex_index")["longueur_m"].sum().reset_index()
    grouped["longueur_km"] = grouped["longueur_m"] / 1000

    # Fusion avec hexagones
    hexagones = hexagones.merge(grouped, on="hex_index", how="left")
    hexagones["longueur_km"] = hexagones["longueur_km"].fillna(0)

    # Export
    hexagones.to_file(output_path)
    print(f"✅ Export effectué : {output_path}")
