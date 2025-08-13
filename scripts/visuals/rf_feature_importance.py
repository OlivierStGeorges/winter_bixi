import geopandas as gpd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

# -------------------
# Variables
# -------------------
colonnes_facteurs = [
    "aire_parc", "nombre_uni", "walkscore_", "transitsco",
    "bikescore_", "longueur_m", "densite_es", "distance_c",
    "densite_lo", #"nb_cegep"
]

# Ton GeoDataFrame (exemple de chargement)
df = gpd.read_file("../../data/processed/ete_2024/hexagones250m_ete_2024_popdens_bikepath_parcs_universites_zonage_logement.shp")
# Ici, j'assume que ton df est déjà chargé et propre

# -------------------
# Séparation features / target
# -------------------
X = df[colonnes_facteurs]
y = df["nb_trajets"]

# -------------------
# Train-test split
# -------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------
# Modèle Random Forest
# -------------------
rf = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
rf.fit(X_train, y_train)

# -------------------
# Feature importances
# -------------------
importances = rf.feature_importances_
feat_importances = pd.Series(importances, index=colonnes_facteurs)

# -------------------
# Graphique
# -------------------
plt.figure(figsize=(8, 5))
feat_importances.sort_values().plot(kind="barh", color="skyblue", edgecolor="black")
plt.title("Importance des variables - RandomForest")
plt.xlabel("Importance")
plt.ylabel("Variables")
plt.tight_layout()
plt.show()
