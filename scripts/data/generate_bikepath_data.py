import geopandas as gpd

def ajouter_longueur_pistes_cyclables_par_hexagone(
    path_hexagones,
    path_reseau,
    output_path,
    epsg=32188  # MTM zone 8
):
    """
       Calcule plusieurs métriques de longueur de pistes cyclables par hexagone.

       Variables créées :
       - longueur_totale_km
       - longueur_totale_4saisons_km
       - longueur_protegee_km
       - longueur_protegee_4saisons_km
       """

    # Charger les fichiers
    hexagones = gpd.read_file(path_hexagones).to_crs(epsg=epsg)
    reseau = gpd.read_file(path_reseau).to_crs(epsg=epsg)

    # Index propre
    hexagones = hexagones.reset_index().rename(columns={"index": "hex_index"})

    # Intersection spatiale
    inter = gpd.overlay(reseau, hexagones, how="intersection")

    # Longueur de chaque segment
    inter["longueur_m"] = inter.geometry.length

    # Colonnes conditionnelles selon tes champs
    inter["longueur_4saisons_m"] = inter["longueur_m"].where(inter["SAISONS4"] == "Oui", 0)
    inter["longueur_4saisons_protegee_m"] = inter["longueur_m"].where(inter["PROTEGE_4S"] == "Oui", 0)

    # Agrégation par hexagone
    grouped = inter.groupby("hex_index").agg(
        longueur_totale_m=("longueur_m", "sum"),
        longueur_totale_4saisons_m=("longueur_4saisons_m", "sum"),
        longueur_protegee_4saisons_m=("longueur_4saisons_protegee_m", "sum")
    ).reset_index()

    # Conversion en km
    for col in grouped.columns[1:]:
        grouped[col.replace("_m", "_km")] = grouped[col] / 1000

    # Fusion avec hexagones
    hexagones = hexagones.merge(grouped, on="hex_index", how="left")

    # Remplir les NaN par 0
    for col in ["longueur_totale_km", "longueur_totale_4saisons_km", "longueur_protegee_4saisons_km"]:
        hexagones[col] = hexagones[col].fillna(0)

    hexagones = hexagones.rename(columns={
        "longueur_totale_m": "long_tot_m",
        "longueur_totale_4saisons_m": "tot_4s_m",
        "longueur_protegee_4saisons_m": "prot_4s_m",
        "longueur_totale_km": "long_tot_km",
        "longueur_totale_4saisons_km": "tot_4s_km",
        "longueur_protegee_4saisons_km": "prot_4s_km"
    })

    # Export
    hexagones.to_file(output_path)
    print(f"✅ Export effectué : {output_path}")
