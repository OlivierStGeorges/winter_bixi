import requests
from dotenv import load_dotenv
import os

# Charger la clé API
load_dotenv()
api_key = os.getenv("WALKSCORE_API_KEY")

def get_walkscore(lat, lon, address, api_key):
    url = "http://api.walkscore.com/score"
    params = {
        'format': 'json',
        'lat': lat,
        'lon': lon,
        'address': address,
        'transit': 1,
        'bike': 1,
        'wsapikey': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
    except Exception as e:
        print(f"Erreur réseau/API : {e}")
        return None

    if response.status_code == 200:
        status = data.get('status')
        if status == 1:
            return {
                'walkscore': data.get('walkscore'),
                'description': data.get('description'),
                'transit_score': data.get('transit', {}).get('score'),
                'bike_score': data.get('bike', {}).get('score')
            }
        elif status == 41:
            print("🚫 Quota atteint (status 41)")
        else:
            print(f"⚠️ Erreur WalkScore: status {status} - {data.get('status_description')}")
    else:
        print(f"❌ Erreur HTTP: {response.status_code}")

    return None

# 🧪 Exemple avec une nouvelle coordonnée (Québec City)
lat = 46.8139
lon = -71.2082
address = "Québec, QC"

score = get_walkscore(lat, lon, address, api_key)
if score:
    print("✅ WalkScore reçu:")
    print(score)
else:
    print("❌ Aucun score reçu.")
