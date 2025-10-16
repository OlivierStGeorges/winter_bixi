import geopandas as gpd

def add_uni_cegep(path_hexagones, output_path):

    # 1. Charger les données
    hexagones = gpd.read_file(path_hexagones)

    hexagones['nb_ec_supp'] = hexagones['nb_cegep'] + hexagones['nombre_uni']

    # 7. Export
    hexagones.to_file(output_path)
