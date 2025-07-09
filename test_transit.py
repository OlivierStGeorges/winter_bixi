import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import re
import unidecode
import time

# 🔧 Convertit une adresse en slug compatible Walkscore
def adresse_to_slug(adresse):
    slug = unidecode.unidecode(adresse)
    slug = re.sub(r"[^\w\s]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.lower()

# 🌍 Géocodage inverse pour obtenir une adresse à partir des coordonnées
def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="walkscore_test_app", timeout=5)
    location = geolocator.reverse((lat, lon), language='en')
    return location.address if location else None

# 📊 Récupère le Walk Score depuis l'API JSON
def get_walkscore_overview(slug):
    url = f"https://www.walkscore.com/auth/_pv/overview/{slug}?d=current"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.walkscore.com/score/{slug}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur JSON pour {slug} : {response.status_code}")
        return None

    data = response.json()
    return {
        "walkscore": data.get("walkscore", -1),
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "title": data.get("title"),
        "url": f"https://www.walkscore.com{data.get('path', '')}"
    }

# 🔍 Récupère Transit Score et Bike Score depuis le HTML
def get_transit_and_bike_score(slug):
    url = f"https://www.walkscore.com/score/{slug}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur HTML pour {slug} : {response.status_code}")
        return -1, -1

    soup = BeautifulSoup(response.text, "lxml")

    transit_img = soup.find("img", src=lambda x: x and "transit/score" in x)
    transit_score = int(re.search(r"(\d+)", transit_img["alt"]).group(1)) if transit_img else -1

    bike_img = soup.find("img", src=lambda x: x and "bike/score" in x)
    bike_score = int(re.search(r"(\d+)", bike_img["alt"]).group(1)) if bike_img else -1

    return transit_score, bike_score

# 📍 Adresse de test (tu peux changer les coordonnées)
lat, lon = 45.5017, -73.5673  # Montréal

adresse = reverse_geocode(lat, lon)
if not adresse:
    print("Adresse introuvable.")
else:
    slug = adresse_to_slug(adresse)
    print(f"\n📍 Adresse : {adresse}")
    print(f"🔗 Slug    : {slug}")

    # Récupérer les scores
    walk_data = get_walkscore_overview(slug)
    transit, bike = get_transit_and_bike_score(slug)

    if walk_data:
        print(f"\n🏠 Adresse : {walk_data['title']}")
        print(f"🚶 Walk Score   : {walk_data['walkscore']}")
        print(f"🚌 Transit Score: {transit}")
        print(f"🚴 Bike Score   : {bike}")
        print(f"🌐 Lien         : {walk_data['url']}")
