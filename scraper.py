import requests
import time
from bs4 import BeautifulSoup

def get_walkscore(slug):
    url = f"https://www.walkscore.com/auth/_pv/overview/{slug}?d=current"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.walkscore.com/score/{slug}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Erreur pour {slug} : {response.status_code}")
            return

        data = response.json()

        print(f"\n🏠 Adresse       : {data.get('title', slug)}")
        print(f"🚶 Walk Score    : {data.get('walkscore', 'Non trouvé')}")
        print(f"🧭 Coordonnées   : ({data.get('lat')}, {data.get('lng')})")
        print(f"🔗 Lien          : https://www.walkscore.com{data.get('path')}")

        return data.get('walkscore', -1)
    except Exception as e:
        print(f"⚠️ Erreur : {e}")
        return -1

def get_transit_and_bike_score(slug):
    url = f"https://www.walkscore.com/score/{slug}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur HTML pour {slug} : {response.status_code}")
        return -1, -1

    soup = BeautifulSoup(response.text, "lxml")
    try:
        transit_img = soup.find("img", src=lambda x: x and "transit/score" in x)
        transit_score = int(re.search(r"(\d+)", transit_img["alt"]).group(1)) if transit_img else -1

        bike_img = soup.find("img", src=lambda x: x and "bike/score" in x)
        bike_score = int(re.search(r"(\d+)", bike_img["alt"]).group(1)) if bike_img else -1
    except Exception as e:
        print('exception')
        return -1, -1

    return transit_score, bike_score

from geopy.geocoders import Nominatim

def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="walkscore_app", timeout=5)
    location = geolocator.reverse((lat, lon), language='en')
    return location.address if location else None

import re
import unidecode

def adresse_to_slug(adresse):
    # Convertir les caractères spéciaux (é → e, etc.)
    slug = unidecode.unidecode(adresse)
    # Remplacer les virgules, points, etc.
    slug = re.sub(r"[^\w\s]", "", slug)
    # Remplacer les espaces par des tirets
    slug = re.sub(r"\s+", "-", slug)
    # Mettre en minuscule
    return slug.lower()


import pandas as pd
df = pd.read_csv("bd_stations_hiver_2023_2024.csv")
df['walkscore'] = 0
df['transitscore'] = 0
df['bikescore'] = 0

for index, row in df.iterrows():
    adresse = reverse_geocode(row['lat'], row['lon'])
    if not adresse:
        print(f"Adresse introuvable pour {row['lat']}, {row['lon']}")
        continue

    slug = adresse_to_slug(adresse)
    walkscore = get_walkscore(slug)
    transitscore, bikescore = get_transit_and_bike_score(slug)

    if walkscore == -1:
        print('walkscore invalide pour adresse',row['lat'], row['lon'], adresse )
    else:
        print('walkscore:', walkscore)
        print('transitscore:', transitscore)
        print('bikescore:', bikescore)

    df.at[index, "walkscore"] = walkscore
    df.at[index, "transitscore"] = transitscore
    df.at[index, "bikescore"] = bikescore
    time.sleep(1.5)  # pour éviter tout blocage (simule un comportement humain)


df.to_csv("bd_stations_hiver_2023_2024_3scores2.csv")