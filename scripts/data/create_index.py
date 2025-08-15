import geopandas as gpd

def create_index(path_hexagones, output_path):

    gdf_input = gpd.read_file(path_hexagones)
    gdf_input = gdf_input.reset_index().rename(columns={"index": "hex_index"})

    gdf_input.to_file(output_path)