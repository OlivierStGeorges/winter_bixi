import geopandas as gpd
import pandas as pd

def calculer_pop_densite_par_hexagone(
    hex_path,
    ad_path,
    output_path,
    colonne_population='COL2',
    crs_proj='EPSG:32188'
):
    # 1. Charger les données
    gdf_hex = gpd.read_file(hex_path)
    gdf_ad = gpd.read_file(ad_path)

    # 2. Reprojection
    gdf_hex = gdf_hex.to_crs(crs_proj)
    gdf_ad = gdf_ad.to_crs(crs_proj)

    # 3. Ajouter un identifiant unique
    gdf_ad = gdf_ad.reset_index().rename(columns={"index": "ad_index"})

    # 4. Préparer les données AD
    gdf_ad["population"] = gdf_ad[colonne_population]
    gdf_ad["aire_ad"] = gdf_ad.geometry.area
    gdf_ad["densite_ad"] = gdf_ad["population"] / gdf_ad["aire_ad"] * 1e6  # hab/km²

    # 5. Intersection hexagones x AD
    inter = gpd.overlay(gdf_hex, gdf_ad, how="intersection")

    # 6. Calcul de l’aire d’intersection
    inter["aire_inter"] = inter.geometry.area

    # 7. Moyenne pondérée des densités par hexagone
    inter["densite_ponderee"] = inter["densite_ad"] * inter["aire_inter"]
    densite_par_hex = (
        inter.groupby("hex_index")
        .agg({"densite_ponderee": "sum", "aire_inter": "sum"})
        .reset_index()
    )
    densite_par_hex["densite_pop_ponderee"] = (
        densite_par_hex["densite_ponderee"] / densite_par_hex["aire_inter"]
    )

    # 8. Fusion avec les hexagones
    gdf_hex = gdf_hex.merge(
        densite_par_hex[["hex_index", "densite_pop_ponderee"]],
        on="hex_index", how="left"
    )
    gdf_hex["densite_es"] = gdf_hex["densite_pop_ponderee"].fillna(0)

    # 9. Export
    gdf_hex.to_file(output_path)

    return gdf_hex
