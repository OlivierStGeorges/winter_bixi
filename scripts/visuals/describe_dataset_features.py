import geopandas as gpd
import numpy as np

# Liste des features à décrire
features = [
    "aire_parc", "nombre_uni", "walkscore_", "transitsco",
    "bikescore_", "l_m", "l4s_m", "p4s_m", "np4s_m",
    "densite_es", "distance_c", "densite_lo", "nb_cegep"
]

# Liste des saisons
seasons = ["ete_2024", "hiver_2324", "hiver_2425"]

for season in seasons:
    # Charger le dataset selon la saison
    if season == "ete_2024":
        hexagones = gpd.read_file(
            "../../data/processed/ete_2024/hexagones250m_ete_2024_popdens_bikepath_parcs_universites_zonage_logement_cegep.shp")
    elif season == "hiver_2324":
        hexagones = gpd.read_file(
            "../../data/processed/hiver_2324/hexagones250m_hiver_2023_2024_popdens_bikepath_parcs_universites_zonage_logement_cegep.shp")
    elif season == "hiver_2425":
        hexagones = gpd.read_file(
            "../../data/processed/hiver2425/hexagones250m_hiver_2024_2025_popdens_bikepath_parcs_universites_zonage_logement_cegep.shp")

    # Sélectionner uniquement les features existantes
    cols = [col for col in features if col in hexagones.columns]

    if not cols:
        print(f"Aucune des features spécifiées n'est présente pour la saison {season}.")
        continue

    hexagones["transitsco"] = hexagones["transitsco"].replace(-1, np.nan)
    # Faire un describe()
    desc = hexagones[cols].describe()

    # Construire le nom de fichier CSV
    output_csv = f"../../output/describe_features_{season}.csv"

    # Sauvegarder le describe dans un CSV
    desc.to_csv(output_csv)

    print(f"Describe saved for {season} -> {output_csv}")
