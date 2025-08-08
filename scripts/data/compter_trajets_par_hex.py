import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def compter_trajets_par_hexagone(
        path_hexagones,
        path_stations,
        output_path,
        epsg_metrique=3857
):
    """
    Associe les stations aux hexagones, compte les trajets, et exporte un fichier GeoSpatial.

    Paramètres :
    - path_hexagones : chemin vers le fichier shapefile des hexagones
    - path_stations  : chemin vers le CSV contenant les stations avec colonnes 'lon', 'lat', 'nb_total'
    - output_path    : chemin de sortie (sans extension pour shapefile, avec pour geojson)
    - epsg_metrique  : système de projection pour l'intersection spatiale (par défaut: EPSG:3857)
    - export_format  : "shp" ou "geojson"
    """

    # Charger les fichiers
    hexagones = gpd.read_file(path_hexagones)
    stations_df = pd.read_csv(path_stations)

    # Créer la géométrie des stations
    geometry = [Point(xy) for xy in zip(stations_df["lon"], stations_df["lat"])]
    stations_gdf = gpd.GeoDataFrame(stations_df, geometry=geometry, crs="EPSG:4326")

    # Reprojeter
    hexagones = hexagones.to_crs(epsg=epsg_metrique)
    stations_gdf = stations_gdf.to_crs(epsg=epsg_metrique)

    # Spatial join
    jointure = gpd.sjoin(stations_gdf, hexagones, how="left", predicate="intersects")

    # Agréger
    somme = jointure.groupby("index_right")["nb_total"].sum()

    # Fusion
    hexagones = hexagones.reset_index(drop=True)
    hexagones["nb_trajets_par_hex"] = hexagones.index.map(somme).fillna(0).astype(int)

    hexagones.to_file(output_path)

    print(f"✅ Export terminé : {output_path}")
