import geopandas as gpd
import pandas as pd

def lister_affectations_par_hexagone(
    hex_path,
    affectation_path,
    output_path,
    colonne_affectation='categorie',
    crs_proj='EPSG:32188'
):
    # 1. Charger les données
    gdf_hex = gpd.read_file(hex_path)
    gdf_affect = gpd.read_file(affectation_path)

    # 2. Reprojection
    gdf_hex = gdf_hex.to_crs(crs_proj)
    gdf_affect = gdf_affect.to_crs(crs_proj)

    # 4. Intersection
    inter = gpd.overlay(gdf_hex, gdf_affect, how="intersection")

    # 5. Extraction des catégories par hexagone
    affectations_par_hex = (
        inter.groupby("hex_index")[colonne_affectation]
        .apply(lambda x: sorted(set(x.dropna())))
        .reset_index()
    )

    # 6. Fusion avec les hexagones
    gdf_hex = gdf_hex.merge(affectations_par_hex, on="hex_index", how="left")
    gdf_hex[colonne_affectation] = gdf_hex[colonne_affectation].apply(
        lambda x: str(x) if isinstance(x, list) else "[]"
    )

    # 7. Export
    gdf_hex.to_file(output_path)

