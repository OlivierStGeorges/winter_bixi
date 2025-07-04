import pandas as pd

df = pd.read_csv("2024_01.csv")

stations  =  df[['STARTSTATIONLONGITUDE', 'STARTSTATIONLATITUDE']].drop_duplicates()
stations_clean = stations[stations['STARTSTATIONLONGITUDE'] < 0]
stations_clean2 = df[df['STARTSTATIONLONGITUDE'] < 0].drop_duplicates(subset=['STARTSTATIONLONGITUDE', 'STARTSTATIONLATITUDE'])
stations_clean3 = df[df['STARTSTATIONLONGITUDE'] < 0].drop_duplicates(subset=['STARTSTATIONNAME'])
stations_clean4 = stations_clean3[stations_clean3['STARTSTATIONNAME'] != 'Parc Plage_Swap eco5']
print(stations_clean4.shape)
print(stations_clean4.columns)
print(stations_clean4[stations_clean4['STARTSTATIONARRONDISSEMENT'] == "Le Plateau-Mont-Royal"].shape)
stations_clean4.to_csv("stations_plateau_01_2024.csv")



