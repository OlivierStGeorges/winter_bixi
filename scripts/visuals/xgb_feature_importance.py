import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split

# -------------------
# Variables
# -------------------
colonnes_facteurs = [
    "aire_parc", "nombre_uni", "walkscore_", "transitsco",
    "bikescore_", "longueur_m", "densite_es", "distance_c",
    "densite_lo", "nb_cegep"
]

# Exemple : chargement des données
#df = gpd.read_file("../../data/processed/ete_2024/hexagones250m_ete_2024_popdens_bikepath_parcs_universites_zonage_logement.shp")
df = gpd.read_file("../../data/processed/hiver_2324/hexagones250m_hiver_2023_2024_popdens_bikepath_parcs_universites_zonage_logement_cegep.shp")
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
    num_boost_round=1000,          # itérations max
    evals=evals,
    early_stopping_rounds=50,      # arrêt si pas d'amélioration
    verbose_eval=False
)

# -------------------
# Importances des features
# -------------------
importances = model.get_score(importance_type="gain")
feat_importances = pd.Series(importances).sort_values()

plt.figure(figsize=(8, 5))
feat_importances.plot(kind="barh", color="skyblue", edgecolor="black")
plt.title("Importance des variables - XGBoost (gain)")
plt.xlabel("Gain moyen par split")
plt.tight_layout()
plt.show()
