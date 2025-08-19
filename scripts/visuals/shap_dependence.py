import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split

# -------------------
# Variables
# -------------------
colonnes_facteurs = [
    "aire_parc", "nombre_uni", "walkscore_", "transitsco",
    "bikescore_", #"longueur_m",
     "densite_es", "distance_c",
    "densite_lo", #"nb_cegep"
]

# Exemple : chargement des données

# Exemple : chargement des données
#df = gpd.read_file("../../data/processed/ete_2024/hexagones250m_ete_2024_popdens_bikepath_parcs_universites_zonage_logement.shp")
#df = gpd.read_file("../../data/processed/hiver_2324/hexagones250m_hiver_2023_2024_popdens_bikepath_parcs_universites_zonage_logement_cegep.shp")
#df = gpd.read_file("../../data/processed/hiver2425/hexagones250m_hiver_2024_2025_popdens_bikepath_parcs_universites_zonage_logement.shp")

# -------------------
# Séparation features / target
# -------------------
X = df[colonnes_facteurs]
y = df["nb_trajets"]

X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------
# Conversion en DMatrix
# -------------------
dtrain = xgb.DMatrix(X_train, label=y_train)
dvalid = xgb.DMatrix(X_valid, label=y_valid)

# -------------------
# Paramètres XGBoost
# -------------------
params = {
    "objective": "reg:squarederror",
    "eta": 0.05,
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "tree_method": "hist",
    "seed": 42
}

# -------------------
# Entraînement avec early stopping
# -------------------
evals = [(dtrain, "train"), (dvalid, "valid")]
model = xgb.train(
    params=params,
    dtrain=dtrain,
    num_boost_round=1000,
    evals=evals,
    early_stopping_rounds=50,
    verbose_eval=False
)

# -------------------
# SHAP Values
# -------------------
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_valid)

# Dependence plot pour la variable "transitsco"
shap.dependence_plot("transitsco", shap_values, X_valid)

import numpy as np

# Nombre de buckets
n_bins = 10

# On récupère les valeurs de la variable et de SHAP
x_vals = X_valid["transitsco"].values
shap_vals = shap_values[:, X_valid.columns.get_loc("transitsco")]

# Découpage en quantiles pour répartir les buckets
bins = pd.qcut(x_vals, q=n_bins, duplicates="drop")

# Moyenne des valeurs SHAP par bucket
bucket_means = pd.DataFrame({
    "bucket": bins,
    "x_val": x_vals,
    "shap_val": shap_vals
}).groupby("bucket").agg({
    "x_val": "mean",
    "shap_val": "mean"
}).reset_index()

# Plot
plt.figure(figsize=(7, 4))
plt.plot(bucket_means["x_val"], bucket_means["shap_val"], marker="o")
plt.title("SHAP dependence (bucketisé) - transitsco")
plt.xlabel("Valeur moyenne de transitsco (par bucket)")
plt.ylabel("Valeur SHAP moyenne")
plt.grid(True)
plt.tight_layout()
plt.show()