import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import re
import unidecode
import random
import geopandas as gpd
from shapely.geometry import Point
import numpy as np

def safe_request_get(url, headers=None, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            else:
                print(f"⚠️ HTTP {response.status_code} sur {url}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erreur réseau (tentative {attempt}/{retries}) : {e}")
        time.sleep(delay)
    print(f"❌ Échec après {retries} tentatives : {url}")
    return None

def reverse_geocode(lat, lon, retries=3):
    geolocator = Nominatim(user_agent="walkscore_app", timeout=5)
    for i in range(retries):
        try:
            location = geolocator.reverse((lat, lon), language='en')
            return location.address if location else None
        except Exception as e:
            print(f"⚠️ Reverse geocoding échoué pour ({lat}, {lon}) : {e}")
            time.sleep(1)
    return None

def adresse_to_slug(adresse):
    slug = unidecode.unidecode(adresse)
    slug = re.sub(r"[^\w\s]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.lower()

def get_walkscore(slug):
    url = f"https://www.walkscore.com/auth/_pv/overview/{slug}?d=current"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.walkscore.com/score/{slug}"
    }

    response = safe_request_get(url, headers=headers)
    if not response:
        return -1

    try:
        data = response.json()
        return data.get('walkscore', -1)
    except Exception as e:
        print(f"❌ Erreur parsing JSON pour {slug} : {e}")
        return -1

def get_transit_and_bike_score(slug):
    url = f"https://www.walkscore.com/score/{slug}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = safe_request_get(url, headers=headers)
    if not response:
        return -1, -1

    soup = BeautifulSoup(response.text, "lxml")
    try:
        transit_img = soup.find("img", src=lambda x: x and "transit/score" in x)
        transit_score = int(re.search(r"(\d+)", transit_img["alt"]).group(1)) if transit_img else -1

        bike_img = soup.find("img", src=lambda x: x and "bike/score" in x)
        bike_score = int(re.search(r"(\d+)", bike_img["alt"]).group(1)) if bike_img else -1

        return transit_score, bike_score
    except Exception as e:
        print(f"❌ Erreur parsing HTML pour {slug} : {e}")
        return -1, -1

def generate_walkscores(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df['walkscore'] = 0
    df['transitscore'] = 0
    df['bikescore'] = 0

    for index, row in df.iterrows():
        adresse = reverse_geocode(row['lat'], row['lon'])
        if not adresse:
            print(f"❌ Adresse introuvable pour {row['lat']}, {row['lon']}")
            continue

        slug = adresse_to_slug(adresse)
        walkscore = get_walkscore(slug)
        transitscore, bikescore = get_transit_and_bike_score(slug)

        if walkscore == -1:
            print(f"❌ Walkscore invalide pour : {adresse}")
        else:
            print(f"✅ {adresse} → Walk: {walkscore} | Transit: {transitscore} | Bike: {bikescore}")

        df.at[index, "walkscore"] = walkscore
        df.at[index, "transitscore"] = transitscore
        df.at[index, "bikescore"] = bikescore

        time.sleep(random.uniform(2, 4))  # éviter blocage

    df.to_csv(output_csv, index=False)
    print(f"✅ Fichier exporté : {output_csv}")

def agg_walkscore_par_hexagone(
    path_hexagones,
    path_walkscore,
    output_path,
    epsg=32188
):
    gdf_hex = gpd.read_file(path_hexagones).to_crs(epsg=epsg)

    points_df = pd.read_csv(path_walkscore)
    cols = ['walkscore', 'transitscore', 'bikescore']
    points_df[cols] = points_df[cols].replace({0: np.nan, -1: np.nan})

    geometry = [Point(xy) for xy in zip(points_df["lon"], points_df["lat"])]
    points_gdf = gpd.GeoDataFrame(points_df, geometry=geometry, crs="EPSG:4326").to_crs(epsg=epsg)

    jointure = gpd.sjoin(points_gdf, gdf_hex, how="left", predicate="intersects")

    moyenne_ws = jointure.groupby("index_right")["walkscore"].mean()
    moyenne_ts = jointure.groupby("index_right")["transitscore"].mean()
    moyenne_bs = jointure.groupby("index_right")["bikescore"].mean()
    moyenne_distance = jointure.groupby("index_right")["distance_to_downtown"].mean()

    gdf_hex["walkscore_moyen"] = gdf_hex.index.map(moyenne_ws)
    gdf_hex["transitscore_moyen"] = gdf_hex.index.map(moyenne_ts)
    gdf_hex["bikescore_moyen"] = gdf_hex.index.map(moyenne_bs)
    gdf_hex["distance_cbd"] = gdf_hex.index.map(moyenne_distance)

    print(gdf_hex[["walkscore_moyen", "transitscore_moyen", "bikescore_moyen"]].describe())

    gdf_hex.to_file(output_path)
    print(f"✅ Export effectué : {output_path}")
