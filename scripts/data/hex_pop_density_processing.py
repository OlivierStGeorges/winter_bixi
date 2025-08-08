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

    # 3. Préparer les données
    gdf_ad['population'] = gdf_ad[colonne_population]
    gdf_hex["hex_id"] = gdf_hex.index.astype(str)

    # 4. Aire des aires de diffusion
    gdf_ad["aire_ad"] = gdf_ad.geometry.area

    # 5. Intersection hexagones x aires
    inter = gpd.overlay(gdf_hex, gdf_ad, how="intersection")

    # 6. Aire des intersections
    inter["aire_inter"] = inter.geometry.area

    # 7. Population transférée à chaque intersection
    inter["pop_inter"] = inter["population"] * (inter["aire_inter"] / inter["aire_ad"])

    # 8. Agrégation par hexagone
    pop_par_hex = inter.groupby("hex_id").agg({"pop_inter": "sum"}).reset_index()

    # 9. Fusion avec les hexagones
    gdf_hex = gdf_hex.merge(pop_par_hex, on="hex_id", how="left")
    gdf_hex["pop_inter"] = gdf_hex["pop_inter"].fillna(0)

    # 10. Densité (hab/km²)
    gdf_hex["aire_hex"] = gdf_hex.geometry.area
    gdf_hex["densite_estimee"] = gdf_hex["pop_inter"] / gdf_hex["aire_hex"] * 1e6

    # 11. Export
    gdf_hex.to_file(output_path)

    return gdf_hex
