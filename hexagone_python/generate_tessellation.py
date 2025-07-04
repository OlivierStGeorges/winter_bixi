import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon
import numpy as np
import math

# ---------------------------
# 1. Charger les points et projeter en mètres
# ---------------------------
# Exemple : CSV avec lat/lon
df = pd.read_csv("somme_stations_plateau_01_2024.csv")
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["STARTSTATIONLONGITUDE"], df["STARTSTATIONLATITUDE"]),
    crs="EPSG:4326"
)
gdf = gdf.to_crs(epsg=3857)

# ---------------------------
# 2. Emprise des points
# ---------------------------
xmin, ymin, xmax, ymax = gdf.total_bounds

# ---------------------------
# 3. Paramètres hexagone
# ---------------------------
r = 250  # rayon en mètres (distance centre à un sommet)
w = 2 * r  # largeur
h = math.sqrt(3) * r  # hauteur (≈ 433m)

cols = int((xmax - xmin) / (w * 0.75)) + 2
rows = int((ymax - ymin) / h) + 2

# ---------------------------
# 4. Génération des hexagones
# ---------------------------
hexes = []
for row in range(rows):
    for col in range(cols):
        x = xmin + col * w * 0.75
        y = ymin + row * h
        if col % 2 == 1:
            y += h / 2  # décalage d'une ligne sur deux

        # Créer un hexagone centré en (x, y)
        hexagon = Polygon([
            (
                x + r * math.cos(math.radians(angle)),
                y + r * math.sin(math.radians(angle))
            )
            for angle in range(0, 360, 60)
        ])
        hexes.append(hexagon)

hexagones = gpd.GeoDataFrame(geometry=hexes, crs="EPSG:3857")

# ---------------------------
# 5. (Optionnel) Filtrer aux points
# ---------------------------
# Garder uniquement les hexagones qui touchent des points
hexagones = hexagones[hexagones.intersects(gdf.unary_union)]
hexagones.to_file("hexagone_python/hexagones_250m.shp", driver="ESRI Shapefile")
