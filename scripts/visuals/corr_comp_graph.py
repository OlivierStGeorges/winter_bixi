import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Dictionnaire x_variable → description
dict_nom = {
    "aire_parc": "Superficie des parcs",
    "nombre_uni": "Nombre d’universités",
    "walk_sc_mo": "Walkscore",
    "tran_sc_mo": "Transitscore",
    "bike_sc_mo": "Bikescore",
    "l_m": "Couverture de pistes cyclables (toutes)",
    "l4s_m": "Couverture de pistes cyclables (4 saisons)",
    "p4s_m": "Couverture de pistes cyclables (protégées - 4 saisons)",
    "np4s_m": "Couverture de pistes cyclables (non protégées - 4 saisons)",
    "densite_es": "Densité de population",
    "distance_c": "Distance au centre-ville",
    "densite_lo": "Densité de logements",
    "nb_cegep": "Nombre de cégeps"
}

# Couleurs et paramètres
colors = ["tab:blue", "tab:orange", "tab:green"]
series_name = ["Été 2024", "Hiver 2023-2024", "Hiver 2024-2025"]
alpha = 0.05
width = 0.25

# Chemins des CSV
files = [
    "../../output/ete_2024/250m/correlations.csv",
    "../../output/hiver_2324/250m/correlations.csv",
    "../../output/hiver_2425/250m/correlations.csv"
]

def plot_correlation(R_col, p_col, output_file="correlations.png"):
    """
    R_col: nom de la colonne des coefficients (ex: "R_pearson")
    p_col: nom de la colonne des p-values (ex: "p_pearson")
    output_file: nom du fichier PNG à sauvegarder
    """
    # Charger les CSV
    dfs = [pd.read_csv(f) for f in files]

    # Labels
    labels = [dict_nom[x] for x in dfs[0]["x_variable"]]
    y = np.arange(len(labels))
    n_series = len(dfs)

    # Extraire valeurs et p-values
    all_R = [df[R_col] for df in dfs]
    all_p = [df[p_col] for df in dfs]

    # Inverser l'ordre pour que bleu soit en haut
    all_R = list(reversed(all_R))
    all_p = list(reversed(all_p))
    colors_reversed = list(reversed(colors))

    # Créer la figure
    fig, ax = plt.subplots(figsize=(10, 8))

    for i, (R, p, color) in enumerate(zip(all_R, all_p, colors_reversed)):
        # Centrer les barres de chaque série autour du tick
        y_positions = y - (n_series-1)/2*width + i*width
        R_sig = [r if pv <= alpha else 0 for r, pv in zip(R, p)]
        R_nonsig = [r if pv > alpha else 0 for r, pv in zip(R, p)]

        # Barres significatives
        ax.barh(y_positions, R_sig, height=width, color=color, edgecolor="black")
        # Barres non significatives
        ax.barh(y_positions, R_nonsig, height=width, color="lightgray", edgecolor="black")

    # Légende
    legend_handles = [
        mpatches.Patch(color="tab:blue", label="Été 2024"),
        mpatches.Patch(color="tab:orange", label="Hiver 2023-2024"),
        mpatches.Patch(color="tab:green", label="Hiver 2024-2025"),
        mpatches.Patch(color="lightgray", label=f"Non significatif (p > {alpha})")
    ]
    ax.legend(handles=legend_handles, loc="best")

    # Mise en forme
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(f"Coefficient R")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Graphique sauvegardé : {output_file}")

# Générer les deux graphiques
plot_correlation(R_col="R", p_col="p_value", output_file="../../output/correlations_comparison_chart_pearson.png")
plot_correlation(R_col="spearman_r", p_col="spearman_p", output_file="../../output/correlations_comparison_chart_spearman.png")
