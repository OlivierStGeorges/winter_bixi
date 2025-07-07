import pandas as pd
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Charger les hexagones (projection en mètres, ex : EPSG:3857)
#hexagones = gpd.read_file("hexagone/GenerateTessellation_nouveau.shp")
#hexagones = gpd.read_file("hexagones_avec_longueur_protégé.shp")
hexagones = gpd.read_file("hexagones_avec_densité.shp")
print(hexagones.columns)
# Exemple : CSV contient les colonnes 'longitude', 'latitude', 'valeur'
points_df = pd.read_csv("data/bd_stations_hiver_2023_2024.csv")
print(points_df.head())

# Créer des géométries (en WGS84 si lon/lat)
geometry = [Point(xy) for xy in zip(points_df["lon"], points_df["lat"])]
points_gdf = gpd.GeoDataFrame(points_df, geometry=geometry, crs="EPSG:4326")

# Reprojeter les points dans le même CRS que les hexagones (ex : EPSG:3857)
#points_gdf = points_gdf.to_crs(hexagones.crs)
# Reprojeter les points et les hexagones dans un système métrique
points_gdf = points_gdf.to_crs(epsg=3857)
hexagones = hexagones.to_crs(epsg=3857)

jointure = gpd.sjoin(points_gdf, hexagones, how="left", predicate="intersects")
print(jointure)


# Group by l'index des hexagones ('index_right') et sommer les valeurs
somme = jointure.groupby("index_right")["nb_total"].sum()
hexagones["nb_trajets_par_hex"] = hexagones.index.map(somme)#.fillna(0)
print(hexagones.columns)
import matplotlib.pyplot as plt
"""
# Taille de la figure
fig, ax = plt.subplots(figsize=(10, 10))

# Tracer les hexagones avec une échelle de couleurs
hexagones.plot(
    column="nb_trajets_par_hex",        # Colonne à colorier
    cmap="OrRd",                  # Colormap (Oranges-Reds)
    linewidth=0.2, edgecolor="grey",
    legend=True,                  # Affiche la légende
    ax=ax
)

# Supprimer les axes pour une carte plus propre
ax.set_axis_off()
ax.set_title("Carte des valeurs par hexagone", fontsize=15)

# Sauvegarder l'image (optionnel)
plt.savefig("hexagones_valeurs.png", dpi=300, bbox_inches="tight")

plt.show()

import matplotlib.pyplot as plt

# Étape 1 — Jointure spatiale (si pas déjà faite)
# (Assure-toi que les CRS sont les mêmes, ex. EPSG:3857)

# jointure = gpd.sjoin(points_gdf, hexagones, how="left", predicate="intersects")

# Étape 2 — Compter les points par hexagone
compte = jointure.groupby("index_right").size()
hexagones["nb_points"] = hexagones.index.map(compte).fillna(0).astype(int)

# Étape 3 — Tracer la carte
fig, ax = plt.subplots(figsize=(10, 10))

hexagones.plot(
    column="nb_points",
    cmap="YlOrRd",
    linewidth=0.2,
    edgecolor="grey",
    legend=True,
    ax=ax
)

# Étape 4 — Ajouter les textes (nombre de points) au centre des hexagones
for idx, row in hexagones.iterrows():
    # Coordonnées du centroïde
    x, y = row.geometry.centroid.coords[0]
    value = row["nb_points"]

    # Afficher uniquement si > 0
    if value > 0:
        ax.text(x, y, str(value), fontsize=8, ha="center", va="center", color="black")

ax.set_title("Nombre de points par hexagone", fontsize=14)
ax.set_axis_off()
plt.tight_layout()
plt.savefig("nb_points_par_hexagone.png", dpi=300)
plt.show()
"""

df = hexagones[["densite_es", "nb_trajets_par_hex"]].dropna()

# Tracer le nuage de points
plt.figure(figsize=(8, 6))
plt.scatter(df["densite_es"], df["nb_trajets_par_hex"], alpha=0.6, color="royalblue", edgecolor="k")

# Ajouter les titres et axes
plt.xlabel("Longueur de piste cyclable (m)")
plt.ylabel("Nombre de déplacements")
plt.title("Relation entre l’offre cyclable et les déplacements (par hexagone)")

# Optionnel : grille
plt.grid(True, linestyle="--", alpha=0.5)

# Sauvegarder l’image (optionnel)
plt.savefig("scatter_cyclable_vs_deplacements.png", dpi=300)

plt.show()

from scipy.stats import pearsonr

# Extraire les variables
x = df["densite_es"]
y = df["nb_trajets_par_hex"]

# Calcul de la corrélation
r, p_value = pearsonr(x, y)

print(f"Coefficient de corrélation linéaire (R) : {r:.3f}")
print(f"P-value associée : {p_value:.3e}")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Suppose que df contient les colonnes suivantes :
# - 'longueur_km' (longueur de pistes cyclables)
# - 'nb_trajets_par_hex' (nombre de déplacements)

# 1. Découper en 5 quantiles (ou change `q=4` pour quartiles, `q=10` pour déciles, etc.)
#df["quantile"] = pd.qcut(df["longueur_m"], q=5, labels=[f"Q{i+1}" for i in range(5)], duplicates="drop")
df["quantile"] = pd.qcut(df["densite_es"], q=5, labels=[f"Q{i+1}" for i in range(5)], duplicates="drop")
# 2. Calcul de la moyenne des déplacements par quantile
grouped = df.groupby("quantile")["nb_trajets_par_hex"].mean().reset_index()

# 3. Tracer un barplot
plt.figure(figsize=(8, 6))
sns.barplot(data=grouped, x="quantile", y="nb_trajets_par_hex", palette="OrRd")

plt.xlabel("Quantile de longueur de pistes cyclables")
plt.ylabel("Nombre moyen de déplacements")
plt.title("Déplacements moyens par niveau d’offre cyclable (quantiles)")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
