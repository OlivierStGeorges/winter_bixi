import geopandas as gpd

def ajouter_longueur_pistes_cyclables_par_hexagone(
    path_hexagones,
    path_reseau,
    output_path,
    epsg=32188
):
    hexagones = gpd.read_file(path_hexagones).to_crs(epsg=epsg)
    reseau = gpd.read_file(path_reseau).to_crs(epsg=epsg)
    print(hexagones.columns)
    #hexagones = hexagones.reset_index().rename(columns={"index": "hex_id"})
    inter = gpd.overlay(reseau, hexagones, how="intersection")
    print(inter.columns)
    inter["l_m"] = inter.geometry.length
    inter["l4s_m"] = inter["l_m"].where(inter["SAISONS4"] == "Oui", 0)
    inter["p4s_m"] = inter["l_m"].where(inter["PROTEGE_4S"] == "Oui", 0)
    inter["np4s_m"] = inter["l4s_m"] - inter["p4s_m"]

    grouped = inter.groupby("hex_index").agg(
        l_m=("l_m", "sum"),
        l4s_m=("l4s_m", "sum"),
        p4s_m=("p4s_m", "sum"),
        np4s_m=("np4s_m", "sum")
    ).reset_index()

    for col in grouped.columns[1:]:
        grouped[col.replace("_m", "_km")] = grouped[col] / 1000

    hexagones = hexagones.merge(grouped, on="hex_index", how="left")
    for col in ["l_km", "l4s_km", "p4s_km", "np4s_km"]:
        hexagones[col] = hexagones[col].fillna(0)

    hexagones.to_file(output_path)
    print(f"✅ Export effectué : {output_path}")
