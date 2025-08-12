import geopandas as gpd
import math

# --- Paramètres ---
shp_path = "../../data/hexagone/tessellation3.shp"
epsg_metrique = 32188  # Montréal - MTM zone 8
#32188 -> 94,90 m
#3857 -> 135,13 m

# --- Chargement ---
gdf = gpd.read_file(shp_path)

# --- Projection en système métrique ---
gdf = gdf.to_crs(epsg=epsg_metrique)

# --- Prendre le premier hexagone ---
hexagon = gdf.geometry.iloc[0]

# --- Calcul de l'aire ---
area = hexagon.area  # en m²

# --- Calcul du rayon (centre -> sommet) ---
radius = math.sqrt((2 * area) / (3 * math.sqrt(3)))

print(f"Aire : {area:.2f} m²")
print(f"Rayon (centre -> sommet) : {radius:.2f} m")
