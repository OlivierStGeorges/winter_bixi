import pandas as pd
import os

def is_in_montreal_region(lat, lon):
    return (lat >= 45.2) & (lat <= 45.8) & (lon >= -74.2) & (lon <= -73.4)

files = {
    "ete_2024": "../../data/processed/ete_2024.csv",
    "hiver_2324": "../../data/processed/hiver_2023_2024.csv",
    "hiver_2425": "../../data/processed/hiver_2024_2025.csv"
}

counts_list = []

for season, filepath in files.items():
    print(f"Traitement de {season}...")
    df = pd.read_csv(filepath)

    # Filtrer trajets hors région Montréal
    mask_start = is_in_montreal_region(df['STARTSTATIONLATITUDE'], df['STARTSTATIONLONGITUDE'])
    mask_end = is_in_montreal_region(df['ENDSTATIONLATITUDE'], df['ENDSTATIONLONGITUDE'])
    in_region = mask_start & mask_end

    df_filtered = df[in_region].copy()

    # Comptage par mois (colonne 'month' existante)
    monthly_counts = df_filtered.groupby('month').size().reset_index(name='count')
    monthly_counts['season'] = season

    counts_list.append(monthly_counts)

# Concaténer tous les résultats
df_counts = pd.concat(counts_list, ignore_index=True)

# Sauvegarder
os.makedirs("output", exist_ok=True)
df_counts.to_csv("output/monthly_trip_counts.csv", index=False)

print("Compilation des déplacements par mois sauvegardée dans output/monthly_trip_counts.csv")
