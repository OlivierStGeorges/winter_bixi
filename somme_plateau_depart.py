import pandas as pd

df = pd.read_csv("2024_01.csv")
stations_plateau = pd.read_csv("stations_plateau_01_2024.csv")

df_plateau = df[df.STARTSTATIONARRONDISSEMENT  == "Le Plateau-Mont-Royal"]

# Compter les trajets par nom de station de départ
df_plateau_somme = df_plateau.groupby("STARTSTATIONNAME").size().reset_index(name="nb_trajets")
df_fusion = pd.merge(
    df_plateau_somme,
    stations_plateau,
    how="left",
    left_on="STARTSTATIONNAME",
    right_on="STARTSTATIONNAME"
)
# Afficher le résultat
print(df_fusion[['STARTSTATIONLONGITUDE', 'STARTSTATIONLATITUDE', 'nb_trajets']])

df_fusion.to_csv("somme_stations_plateau_01_2024.csv")