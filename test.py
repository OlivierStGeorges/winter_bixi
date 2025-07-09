from geopy.geocoders import Nominatim
import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("WALKSCORE_API_KEY")


def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="walkscore_app")
    location = geolocator.reverse((lat, lon), language='en')
    return location.address if location else None

def get_walkscore(lat, lon, api_key):
    address = reverse_geocode(lat, lon)
    print(address)
    if not address:
        print("Impossible d’obtenir une adresse approximative.")
        return None

    url = "http://api.walkscore.com/score"
    params = {
        'format': 'json',
        'lat': lat,
        'lon': lon,
        'address': address,
        'wsapikey': api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200 and data.get('status') == 1:
        return {
            'walkscore': data.get('walkscore'),
            'description': data.get('description'),
            'transit_score': data.get('transit', {}).get('score'),
            'bike_score': data.get('bike', {}).get('score')
        }
    else:
        print(f"Erreur: {data.get('status')} - {data.get('status_description', 'Unknown error')}")
        return None

# Exemple d’utilisation :
lat = 45.51025293429709
lon = -73.55677664279938

score = get_walkscore(lat, lon, api_key)
if score:
    print(score)