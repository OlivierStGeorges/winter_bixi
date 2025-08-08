from math import radians, sin, cos, sqrt, atan2
import pandas as pd

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Rayon de la Terre en km

    # Convertir degrés -> radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def compute_distance_to_downtown(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    #calculate distance to Place Ville-Marie
    df['distance_to_downtown'] = df.apply(lambda x: haversine(x.lat, x.lon, 45.500533,  -73.569588), axis=1)

    df.to_csv(output_csv, index=False)

