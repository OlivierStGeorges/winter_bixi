import geopandas as gpd

def ajouter_surface_parcs_par_hexagone(
    path_hexagones,
    path_parcs,
    output_path,
    epsg=32188
):
    """
    Calcule la surface de parc présente dans chaque hexagone et exporte le fichier enrichi.

    Paramètres :
    - path_hexagones : chemin du fichier des hexagones (shp ou geojson)
    - path_parcs     : chemin du fichier des parcs (polygones)
    - output_path    : chemin du fichier de sortie
    - epsg           : projection en mètres pour calcul d'aires (par défaut : 32188 - MTM zone 8)
    """
    # Charger les fichiers
    gdf_hex = gpd.read_file(path_hexagones)
    gdf_parc = gpd.read_file(path_parcs)

    # Reprojection en mètres
    gdf_hex = gdf_hex.to_crs(epsg=epsg)
    gdf_parc = gdf_parc.to_crs(epsg=epsg)

    # Ajouter ID unique aux hexagones
    gdf_hex["hex_id"] = gdf_hex.index.astype(str)

    # Calculer l'aire des polygones de parc
    gdf_parc["aire_parc"] = gdf_parc.geometry.area

    # Intersection spatiale
    inter = gpd.overlay(gdf_hex, gdf_parc, how="intersection")

    # Calcul de l’aire intersectée
    inter["aire_inter"] = inter.geometry.area

    # Agrégation par hexagone
    aire_par_hex = inter.groupby("hex_id")["aire_inter"].sum().reset_index()

    # Fusion avec la grille d’origine
    gdf_hex = gdf_hex.merge(aire_par_hex, on="hex_id", how="left")
    gdf_hex["aire_parc"] = gdf_hex["aire_inter"].fillna(0)

    # Export du fichier enrichi
    gdf_hex.to_file(output_path)
    print(f"✅ Export effectué : {output_path}")
