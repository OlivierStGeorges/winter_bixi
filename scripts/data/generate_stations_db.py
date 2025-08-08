import pandas as pd

def agg_data_by_station(df):
    # Filtrer les coordonnées valides
    df = df[df['STARTSTATIONLONGITUDE'] < 0]
    df = df[df['ENDSTATIONLONGITUDE'] < 0]

    # Groupby sur les départs
    depart = df.groupby('STARTSTATIONNAME').agg(
        nb_depart=('STARTTIMEMS', 'count'),
        lon=('STARTSTATIONLONGITUDE', 'first'),
        lat=('STARTSTATIONLATITUDE', 'first'),
        arrondissement=('STARTSTATIONARRONDISSEMENT', 'first')
    ).reset_index()

    # Groupby sur les arrivées
    arrivee = df.groupby('ENDSTATIONNAME').agg(
        nb_arrivee=('ENDTIMEMS', 'count'),
        lon_end=('ENDSTATIONLONGITUDE', 'first'),
        lat_end=('ENDSTATIONLATITUDE', 'first')
    ).reset_index()

    # Merge des deux tables
    stations = pd.merge(
        depart, arrivee,
        left_on='STARTSTATIONNAME', right_on='ENDSTATIONNAME',
        how='outer'
    )

    # Fusion des noms et coordonnées
    stations['station'] = stations['STARTSTATIONNAME'].combine_first(stations['ENDSTATIONNAME'])
    stations['lon'] = stations['lon'].combine_first(stations['lon_end'])
    stations['lat'] = stations['lat'].combine_first(stations['lat_end'])

    # Gérer les NaN et calculer total
    stations['nb_depart'] = stations['nb_depart'].fillna(0).astype(int)
    stations['nb_arrivee'] = stations['nb_arrivee'].fillna(0).astype(int)
    stations['nb_total'] = stations['nb_depart'] + stations['nb_arrivee']

    stations['arrondissement'] = stations['arrondissement'].fillna("Inconnu")

    stations_final = stations[['station', 'lon', 'lat', 'arrondissement', 'nb_depart', 'nb_arrivee', 'nb_total']]

    return stations_final

def generate_stations_db(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    stations_db = agg_data_by_station(df)
    stations_db.to_csv(output_csv, index=False)
