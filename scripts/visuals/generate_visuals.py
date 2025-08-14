import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import os
import numpy as np
from scipy.stats import spearmanr
import mapclassify

def analyser_relation(df, x_col, y_col, output_prefix, correlation_csv="../../output/correlations.csv"):
    data = df[[x_col, y_col]].copy()
    data = data.replace([-1], pd.NA).dropna()

    r_sp, p_sp = spearmanr(data[x_col], data[y_col])

    # Corrélation de Pearson
    r, p_value = pearsonr(data[x_col], data[y_col])
    print(f"{output_prefix} - R: {r:.3f}, p-value: {p_value:.3e}")

    # Export corrélation dans CSV (append ou création)
    corr_df = pd.DataFrame([{
        "x_variable": x_col,
        "y_variable": y_col,
        "R": round(r, 4),
        "p_value": p_value,
        "n_obs": len(data),
        "spearman_r": round(r_sp, 4),
        "spearman_p": p_sp
    }])


    os.makedirs("../../output", exist_ok=True)
    if os.path.exists(correlation_csv):
        corr_df.to_csv(correlation_csv, mode="a", header=False, index=False)
    else:
        corr_df.to_csv(correlation_csv, index=False)

    # Scatterplot
    plt.figure(figsize=(8, 6))
    plt.scatter(data[x_col], data[y_col], alpha=0.6, color="royalblue", edgecolor="k")
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f"{y_col} vs {x_col}\nR = {r:.2f}, p = {p_value:.2e}")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"../../output/{output_prefix}_scatter.png", dpi=300)
    plt.close()

    # Classer avec Jenks
    classifier = mapclassify.NaturalBreaks(data[x_col], k=5)
    bins = [-float("inf")] + list(classifier.bins)  # inclure min
    data["bin_jenks"] = pd.cut(data[x_col], bins=bins, include_lowest=True)

    # Grouper : taille et moyenne
    grouped = data.groupby("bin_jenks").agg(
        n_obs=(x_col, "count"),
        mean_trajets=(y_col, "mean")
    ).reset_index()

    # --- Graph ---
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Histogramme des obs
    ax1.bar(grouped["bin_jenks"].astype(str), grouped["n_obs"], color="skyblue", alpha=0.7,
            label="Nombre d'observations")
    ax1.set_ylabel("Nombre d'observations", color="skyblue")
    ax1.tick_params(axis="y", labelcolor="skyblue")
    ax1.set_xlabel("Bin Jenks")

    # Courbe pour le nb moyen de trajets
    ax2 = ax1.twinx()
    ax2.plot(grouped["bin_jenks"].astype(str), grouped["mean_trajets"], color="darkred", marker="o",
             label="Nb trajets moyen")
    ax2.set_ylabel("Nombre moyen de trajets", color="darkred")
    ax2.tick_params(axis="y", labelcolor="darkred")

    plt.title("Observations et trajets moyens par bin (Jenks)")
    fig.tight_layout()
    plt.savefig(f"../../output/{output_prefix}_jenks.png", dpi=300)
    plt.close()

    # Barplot par quantiles
    data["quantile"] = pd.qcut(data[x_col], q=5, duplicates="drop")
    grouped = data.groupby("quantile")[y_col].mean().reset_index()

    plt.figure(figsize=(8, 6))
    sns.barplot(data=grouped, x="quantile", y=y_col, palette="OrRd")
    plt.xlabel(f"Quantile de {x_col}")
    plt.ylabel(f"Moyenne de {y_col}")
    plt.title(f"{y_col} moyen selon {x_col} (par quantiles)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"../../output/{output_prefix}_barplot.png", dpi=300)
    plt.close()

    # Histogramme de x_col
    plt.figure(figsize=(8, 5))
    sns.histplot(data[x_col], kde=True, color="skyblue", edgecolor="k")
    plt.title(f"Distribution de {x_col}")
    plt.xlabel(x_col)
    plt.ylabel("Fréquence")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"../../output/{output_prefix}_hist_{x_col}.png", dpi=300)
    plt.close()

def generer_matrice_correlation(df, colonnes, output_path="../../output/correlation_matrix.png"):
    """
    Calcule et trace la matrice de corrélation entre les colonnes spécifiées.

    Args:
        df (pd.DataFrame): Le DataFrame contenant les variables.
        colonnes (list): Liste des colonnes à inclure dans la matrice.
        output_path (str): Chemin pour sauvegarder l'image.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np

    # Filtrer uniquement les colonnes numériques et valides
    data = df[colonnes].replace(-1, np.nan).dropna()

    # Calcul de la matrice de corrélation
    corr_matrix = data.corr(method="pearson")

    # Plot
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0, square=True,
                cbar_kws={"shrink": 0.8}, linewidths=0.5, linecolor="gray")
    plt.title("Matrice de corrélation (Pearson)")
    plt.tight_layout()

    # Sauvegarde
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()

def analyser_zonage(hexagones, output_path ):
    import ast

    # 2. Convertir la chaîne de liste en vraie liste Python
    hexagones['categorie'] = hexagones['categorie'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

    # 3. Exploser pour une ligne par (hexagone, categorie)
    df_exploded = hexagones.explode('categorie')

    # 4. Agréger par catégorie : moyenne des trajets
    df_grp = df_exploded.groupby('categorie')['nb_trajets'].mean().sort_values(ascending=False)

    # 5. Graphique
    plt.figure(figsize=(10, 6))
    df_grp.plot(kind='barh')
    plt.xlabel("Nombre moyen de trajets par hexagone")
    plt.ylabel("Catégorie d'affectation du sol")
    plt.title("Influence des catégories d'affectation du sol sur les trajets")
    plt.gca().invert_yaxis()
    plt.tight_layout()


    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    # Chargement des données
    season = "hiver_2324"
    if season == "ete_2024":
        hexagones = gpd.read_file("../../data/processed/ete_2024/hexagones250m_ete_2024_popdens_bikepath_parcs_universites_zonage_logement_cegep.shp")
    elif season == "hiver_2324":
        hexagones = gpd.read_file("../../data/processed/hiver_2324/hexagones250m_hiver_2023_2024_popdens_bikepath_parcs_universites_zonage_logement_cegep.shp")
    elif season == "hiver_2425":
        hexagones = gpd.read_file("../../data/processed/hiver2425/hexagones250m_hiver_2024_2025_popdens_bikepath_parcs_universites_zonage_logement.shp")
    print(hexagones.columns)
    import numpy as np
    hexagones["transitsco"] = hexagones["transitsco"].replace(-1, np.nan)
    season = season + "/250m"
    # Lancer l'analyse sur différentes variables
    analyser_relation(hexagones, "aire_parc", "nb_trajets", f"{season}/parc_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "nombre_uni", "nb_trajets", f"{season}/nb_universite_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "walkscore_", "nb_trajets", f"{season}/walkscore_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "transitsco", "nb_trajets", f"{season}/transitscore_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "bikescore_", "nb_trajets", f"{season}/bikescore_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "l_m", "nb_trajets", f"{season}/longueur_piste_cyclable_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "l4s_m", "nb_trajets", f"{season}/longueur_piste_cyclable_4saisons_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "p4s_m", "nb_trajets", f"{season}/longueur_piste_cyclable_4saisons_protege_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "np4s_m", "nb_trajets", f"{season}/longueur_piste_cyclable_4saisons_non_protege_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "densite_es", "nb_trajets", f"{season}/densite_population_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "distance_c", "nb_trajets", f"{season}/distance_centre-ville_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "densite_lo", "nb_trajets", f"{season}/densite_logements_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_relation(hexagones, "nb_cegep", "nb_trajets", f"{season}/nb_cegep_vs_trajets",
                      correlation_csv=f"../../output/{season}/correlations.csv")

    analyser_zonage(hexagones, output_path=f"../../output/{season}/zonage.png")

    colonnes_facteurs = [
        "aire_parc", "nombre_uni", "walkscore_", "transitsco",
        "bikescore_", "l_m", "l4s_m", "p4s_m", "np4s_m", "densite_es", "distance_c", "densite_lo", "nb_cegep"
    ]

    generer_matrice_correlation(hexagones, colonnes_facteurs,
                                output_path=f"../../output/{season}/matrice_correlation_facteurs.png")


if __name__ == "__main__":
    main()
