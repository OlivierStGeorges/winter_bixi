import pandas as pd
import numpy as np
import os
from scipy import stats

def haversine_vectorized(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # km
    return c * r

def is_in_montreal_region(lat, lon):
    return (lat >= 45.2) & (lat <= 45.8) & (lon >= -74.2) & (lon <= -73.4)

files = {
    "ete_2024": "../../data/processed/ete_2024.csv",
    "hiver_2324": "../../data/processed/hiver_2023_2024.csv",
    "hiver_2425": "../../data/processed/hiver_2024_2025.csv"
}

outlier_dir = "outliers/"
os.makedirs(outlier_dir, exist_ok=True)

stats_list = []
all_filtered = []  # va contenir toutes les lignes filtrées

for season, file in files.items():
    print(f"Traitement de {season}...")
    df = pd.read_csv(file)

    df['travel_distance'] = haversine_vectorized(
        df['STARTSTATIONLATITUDE'], df['STARTSTATIONLONGITUDE'],
        df['ENDSTATIONLATITUDE'], df['ENDSTATIONLONGITUDE']
    )

    mask_start = is_in_montreal_region(df['STARTSTATIONLATITUDE'], df['STARTSTATIONLONGITUDE'])
    mask_end = is_in_montreal_region(df['ENDSTATIONLATITUDE'], df['ENDSTATIONLONGITUDE'])
    in_region = mask_start & mask_end

    # Outliers hors région
    outliers_region = df[~in_region]
    if not outliers_region.empty:
        file_out_region = os.path.join(outlier_dir, f"{season}_hors_region.csv")
        outliers_region.to_csv(file_out_region, index=False)
        print(f"  {len(outliers_region)} trajets hors région sauvegardés dans {file_out_region}")

    # Outliers distance > 1000km (dans la région)
    outliers_dist = df[(in_region) & (df['travel_distance'] > 1000)]
    if not outliers_dist.empty:
        file_out_dist = os.path.join(outlier_dir, f"{season}_outliers_distance.csv")
        outliers_dist.to_csv(file_out_dist, index=False)
        print(f"  {len(outliers_dist)} trajets >1000 km sauvegardés dans {file_out_dist}")

    # Garde que les trajets dans la région ET avec distance <= 1000 km et != 0
    df_filtered = df[in_region & (df['travel_distance'] <= 1000) & (df['travel_distance'] != 0)]
    df_filtered['season'] = season
    all_filtered.append(df_filtered)

    # Calcul stats travel_distance
    df_stats = df_filtered['travel_distance'].describe(percentiles=[0.25, 0.5, 0.75]).to_frame().T
    df_stats['season'] = season
    cols = ['season'] + [c for c in df_stats.columns if c != 'season']
    df_stats = df_stats[cols]
    stats_list.append(df_stats)

# Sauvegarde des stats
df_stats = pd.concat(stats_list, ignore_index=True)
os.makedirs("../../output", exist_ok=True)
stats_file = "../../output/travel_distance_stats_filtered_sans0.csv"
df_stats.to_csv(stats_file, index=False)
print(f"\nStats globales sauvegardées dans {stats_file}")
print(df_stats)

# Concaténer toutes les lignes filtrées
df_all = pd.concat(all_filtered, ignore_index=True)

# Regrouper hiver ensemble pour comparaison
df_all['saison_type'] = df_all['season'].apply(lambda x: 'ete' if 'ete' in x else 'hiver')

dist_ete = df_all[df_all['saison_type'] == 'ete']['travel_distance']
dist_hiver = df_all[df_all['saison_type'] == 'hiver']['travel_distance']

# Test t de Welch
t_stat, p_val = stats.ttest_ind(dist_ete, dist_hiver, equal_var=False)

print("\n=== Test t Welch Été vs Hiver ===")
print(f"t = {t_stat:.3f}, p = {p_val:.3e}")
if p_val < 0.05:
    print("=> Différence significative (p < 0.05)")
else:
    print("=> Pas de différence significative")
