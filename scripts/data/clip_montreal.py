import geopandas as gpd


def clip_mtl(input_path, clip_path, output_path, crs_proj="EPSG:32188"):
    """
    Découpe un fichier vectoriel (input_path) en utilisant un autre fichier (clip_path).
    Sauvegarde le résultat dans output_path, reprojeté dans crs_proj.

    Paramètres
    ----------
    input_path : str
        Chemin du fichier à découper (ex: "input.shp").
    clip_path : str
        Chemin du fichier qui sert de masque (ex: "clip.shp").
    output_path : str
        Chemin du fichier de sortie (ex: "output.shp").
    crs_proj : str, optionnel
        Code EPSG ou proj string du système de coordonnées cible (par défaut "EPSG:32188").
    """

    # Charger les fichiers
    gdf_input = gpd.read_file(input_path)
    gdf_clip = gpd.read_file(clip_path)

    # Reprojeter le masque au CRS de la couche d’entrée
    if gdf_input.crs != gdf_clip.crs:
        gdf_clip = gdf_clip.to_crs(gdf_input.crs)

    # Effectuer le clip
    gdf_clipped = gpd.clip(gdf_input, gdf_clip)

    # Reprojeter le résultat dans le CRS demandé
    gdf_clipped = gdf_clipped.to_crs(crs_proj)

    # Sauvegarder
    gdf_clipped.to_file(output_path)

    print(f"✅ Clip terminé. Résultat enregistré dans {output_path} avec CRS {crs_proj}")
