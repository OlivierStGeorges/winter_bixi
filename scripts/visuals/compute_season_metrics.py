import pandas as pd
import numpy as np
"""

def haversine_vectorized(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Rayon de la Terre en km
    return c * r


files = {
    "ete_2024": "../../data/processed/ete_2024.csv",
    "hiver_2324": "../../data/processed/hiver_2023_2024.csv",
    "hiver_2425": "../../data/processed/hiver_2024_2025.csv"
}

stats_list = []

for season, file in files.items():
    print(f"Traitement de {season} ({file})...")
    df = pd.read_csv(file)

    df['travel_distance'] = haversine_vectorized(
        df['STARTSTATIONLATITUDE'],
        df['STARTSTATIONLONGITUDE'],
        df['ENDSTATIONLATITUDE'],
        df['ENDSTATIONLONGITUDE']
    )
    print(df[df['travel_distance']  > 1000].shape)

    print(df[df['travel_distance']  > 1000])
    df = df[df['travel_distance'] < 1000]
    desc = df['travel_distance'].describe()
    # On crée un dict avec les stats + saison
    stats = desc.to_dict()
    stats['season'] = season

    stats_list.append(stats)

# Crée un DataFrame à partir des stats
df_stats = pd.DataFrame(stats_list)

# Réorganise les colonnes pour que 'season' soit la première
cols = ['season'] + [col for col in df_stats.columns if col != 'season']
df_stats = df_stats[cols]

# Sauvegarde dans CSV
df_stats.to_csv("output/travel_distance_stats.csv", index=False)

print("Stats sauvegardées dans travel_distance_stats.csv")
print(df_stats)


"""
"""
import pandas as pd
import numpy as np
import os


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
output_dir = "outliers/"
os.makedirs(output_dir, exist_ok=True)

for season, file in files.items():
    print(f"Traitement de {season}...")
    df = pd.read_csv(file)
    size_avant = df.shape[0]
    # Filtrer uniquement les trajets où les 2 points sont dans Montréal
    mask_start = is_in_montreal_region(df['STARTSTATIONLATITUDE'], df['STARTSTATIONLONGITUDE'])
    mask_end = is_in_montreal_region(df['ENDSTATIONLATITUDE'], df['ENDSTATIONLONGITUDE'])
    df = df[mask_start & mask_end]
    print("outliers filtered", size_avant - df.shape[0])
    df['travel_distance'] = haversine_vectorized(
        df['STARTSTATIONLATITUDE'], df['STARTSTATIONLONGITUDE'],
        df['ENDSTATIONLATITUDE'], df['ENDSTATIONLONGITUDE']
    )

    # Extraire les outliers > 1000 km
    outliers = df[df['travel_distance'] > 1000]
    if not outliers.empty:
        outlier_file = os.path.join(output_dir, f"{season}_outliers.csv")
        outliers.to_csv(outlier_file, index=False)
        print(f"  {len(outliers)} outliers (>1000km) sauvegardés dans {outlier_file}")
    else:
        print("  Aucun outlier > 1000 km trouvé.")
"""

import pandas as pd
import numpy as np
import os


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
    else:
        print("  Aucun trajet hors région")

    # Outliers distance > 1000km (dans la région)
    outliers_dist = df[(in_region) & (df['travel_distance'] > 1000)]
    if not outliers_dist.empty:
        file_out_dist = os.path.join(outlier_dir, f"{season}_outliers_distance.csv")
        outliers_dist.to_csv(file_out_dist, index=False)
        print(f"  {len(outliers_dist)} trajets >1000 km sauvegardés dans {file_out_dist}")
    else:
        print("  Aucun trajet > 1000 km dans la région")

    # Garde que les trajets dans la région ET avec distance <= 1000 km
    df_filtered = df[in_region & (df['travel_distance'] <= 1000) & (df['travel_distance'] != 0)]

    # Calcul stats travel_distance
    stats = df_filtered['travel_distance'].describe(percentiles=[0.25, 0.5, 0.75]).to_frame().T
    stats['season'] = season

    # Réorganiser colonnes (season en premier)
    cols = ['season'] + [c for c in stats.columns if c != 'season']
    stats = stats[cols]

    stats_list.append(stats)

# Concat stats toutes saisons
df_stats = pd.concat(stats_list, ignore_index=True)

# Sauvegarder stats dans CSV
stats_file = "../../output/travel_distance_stats_filtered_sans0.csv"
df_stats.to_csv(stats_file, index=False)
print(f"\nStats globales sauvegardées dans {stats_file}")
