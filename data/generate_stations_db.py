import pandas as pd

def extract_stations(df):
    stations = df[['STARTSTATIONLONGITUDE', 'STARTSTATIONLATITUDE']].drop_duplicates()
    stations_clean = stations[stations['STARTSTATIONLONGITUDE'] < 0]
    stations_clean2 = df[df['STARTSTATIONLONGITUDE'] < 0].drop_duplicates(
        subset=['STARTSTATIONLONGITUDE', 'STARTSTATIONLATITUDE'])
    stations_clean3 = df[df['STARTSTATIONLONGITUDE'] < 0].drop_duplicates(subset=['STARTSTATIONNAME'])
    stations_clean4 = stations_clean3[stations_clean3['STARTSTATIONNAME'] != 'Parc Plage_Swap eco5']
    return stations_clean4


df = pd.read_csv("2024_01.csv")
stations = extract_stations(df)
