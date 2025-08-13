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
    "bikescore_", "longueur_m", "densite_es", "distance_c",
    "densite_lo",# "nb_cegep"
]

# Exemple : chargement des données
df = gpd.read_file("../../data/processed/ete_2024/hexagones250m_ete_2024_popdens_bikepath_parcs_universites_zonage_logement.shp")
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
# Conversion en DMatrix (format interne XGBoost)
# -------------------
dtrain = xgb.DMatrix(X_train, label=y_train)
dvalid = xgb.DMatrix(X_valid, label=y_valid)

# -------------------
# Paramètres du modèle
# -------------------
params = {
    "objective": "reg:squarederror",
    "eta": 0.05,           # learning_rate
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "tree_method": "hist", # plus rapide pour gros jeux de données
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

# Graphique global : importance moyenne absolue
shap.summary_plot(shap_values, X_valid, plot_type="bar")

# Graphique global détaillé (impact positif/négatif)
shap.summary_plot(shap_values, X_valid)
