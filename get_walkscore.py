from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os
from walkscore import WalkScoreAPI

load_dotenv()
api_key = os.getenv("WALKSCORE_API_KEY")
walkscore_api = WalkScoreAPI(api_key = api_key)

def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="walkscore_app")
    location = geolocator.reverse((lat, lon), language='en')
    return location.address if location else None

def get_walkscore(lat, lon):
    address = reverse_geocode(lat, lon)
    print(lat, lon, address)
    result = walkscore_api.get_score(latitude = lat, longitude = lon, address = address)


lat = 45.51025293429709
lon = -73.55677664279938

score = get_walkscore(lat, lon)
print(score)

#import pandas as pd

#df = pd.read_csv('data/bd_stations_hiver_2024_2025.csv')
#print(df.columns)
#
#df['walkscore'] = 0
#import time
#for index, row in df.iterrows():
#    time.sleep(1)
#    row['walkscore'] = get_walkscore(row['lat'], row['lon'])
#df.to_csv('data/bd_stations_hiver_2024_2025_with_walkscore.csv')