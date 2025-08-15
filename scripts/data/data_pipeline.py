from generate_datasets import generate_dataset
from generate_stations_db import generate_stations_db
from walkscore_processing import generate_walkscores, agg_walkscore_par_hexagone
from hex_pop_density_processing import calculer_pop_densite_par_hexagone
from compter_trajets_par_hex import compter_trajets_par_hexagone
from generate_bikepath_data import ajouter_longueur_pistes_cyclables_par_hexagone
from generate_park_density_data import ajouter_surface_parcs_par_hexagone
from add_university_data import ajouter_nombre_universites_par_hexagone
from compute_distance_to_downtown import compute_distance_to_downtown
from add_zoning_data import lister_affectations_par_hexagone
from generate_housing_density_data import calculer_densite_logement_par_hexagone
from add_college_data import ajouter_nombre_cegep_par_hexagone
from clip_montreal import clip_mtl
from create_index import create_index
import yaml

def load_config(path="config_ete_2024.yml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    steps = config["run_steps"]
    paths = config["paths"]

    if steps["generate_dataset"]:
        generate_dataset(
            config["season"],
            paths["year_dataset"],
            paths["previous_year_dataset"],
            paths["dataset_output"]
        )

    if steps["generate_stations_db"]:
        generate_stations_db(
            paths["bd_stations_input"],
            paths["bd_stations_output"]
        )

    if steps["generate_walkscores"]:
        generate_walkscores(
            paths["walkscore_input"],
            paths["walkscore_output"]
        )

    if steps["compute_distance_to_downtown"]:
        compute_distance_to_downtown(
            paths['walkscore_output'],
            paths['distance_output']
        )

    create_index(paths["hexagone"], paths['hex_index'])

    if steps["aggregate_walkscores"]:
        agg_walkscore_par_hexagone(
            path_hexagones=paths["hex_index"],
            path_walkscore=paths["distance_output"],
            output_path=paths["hex_walkscore"],
        )

    if steps["compter_trajets"]:
        compter_trajets_par_hexagone(
            path_hexagones=paths["hex_walkscore"],
            path_stations=paths["distance_output"],
            output_path=paths["hex_nb_trajets"]
        )
    if steps['clip_mtl']:
        clip_mtl(
            input_path=paths["hex_nb_trajets"],
            clip_path=paths["clip_mtl_polygon"],
            output_path=paths["hex_clip"]
        )
        paths['hex_nb_trajets'] = paths['hex_clip']

    if steps["pop_density"]:
        calculer_pop_densite_par_hexagone(
            hex_path=paths["hex_nb_trajets"],
            ad_path=paths["aire_diffusion"],
            output_path=paths["hex_popdens"]
        )

    if steps["bikepath_length"]:
        ajouter_longueur_pistes_cyclables_par_hexagone(
            path_hexagones=paths["hex_popdens"],
            path_reseau=paths["reseau_cyclable"],
            output_path=paths["hex_bikepath"]
        )

    if steps["park_surface"]:
        ajouter_surface_parcs_par_hexagone(
            path_hexagones=paths["hex_bikepath"],
            path_parcs=paths["parcs"],
            output_path=paths["hex_park"]
        )

    if steps["universites"]:
        ajouter_nombre_universites_par_hexagone(
            path_hexagones=paths["hex_park"],
            path_universites=paths["universites"],
            output_path=paths["hex_universites"]
        )

    if steps["zonage"]:
        lister_affectations_par_hexagone(
            hex_path=paths["hex_universites"],
            affectation_path=paths["affectation"],
            output_path=paths["hex_zonage"]
        )

    if steps["densite_logement"]:
        calculer_densite_logement_par_hexagone(
            hex_path=paths["hex_zonage"],
            ad_path=paths["aire_diffusion_logements"],
            output_path=paths["hex_logement"],
        )
    if steps["cegep"]:
        ajouter_nombre_cegep_par_hexagone(
            path_hexagones=paths["hex_logement"],
            path_cegep=paths["cegep"],
            output_path=paths["hex_cegep"]
        )

if __name__ == "__main__":
    main()
