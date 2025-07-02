import pandas as pd
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Charger les hexagones (projection en mètres, ex : EPSG:3857)
hexagones = gpd.read_file("hexagone/GenerateTessellation2.shp")
print(hexagones.crs)
# Exemple : CSV contient les colonnes 'longitude', 'latitude', 'valeur'
points_df = pd.read_csv("somme_stations_plateau_01_2024.csv")
print(points_df.head())

# Créer des géométries (en WGS84 si lon/lat)
geometry = [Point(xy) for xy in zip(points_df["STARTSTATIONLONGITUDE"], points_df["STARTSTATIONLATITUDE"])]
points_gdf = gpd.GeoDataFrame(points_df, geometry=geometry, crs="EPSG:4326")

# Reprojeter les points dans le même CRS que les hexagones (ex : EPSG:3857)
#points_gdf = points_gdf.to_crs(hexagones.crs)
# Reprojeter les points et les hexagones dans un système métrique
points_gdf = points_gdf.to_crs(epsg=3857)
hexagones = hexagones.to_crs(epsg=3857)

jointure = gpd.sjoin(points_gdf, hexagones, how="left", predicate="within")

# Group by l'index des hexagones ('index_right') et sommer les valeurs
somme = jointure.groupby("index_right")["nb_trajets"].sum()
hexagones["nb_trajets"] = hexagones.index.map(somme).fillna(0)

import matplotlib.pyplot as plt

# Taille de la figure
fig, ax = plt.subplots(figsize=(10, 10))

# Tracer les hexagones avec une échelle de couleurs
hexagones.plot(
    column="nb_trajets",        # Colonne à colorier
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
