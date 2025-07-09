import pandas as pd

df = pd.read_csv("bd_stations_hiver_2023_2024_3scores.csv")
print(df.columns)
#print(df[])

print(df[df['walkscore'] > 100 ][['lat', 'lon']])

print(df[df['transitscore'] > 100 ][['lat', 'lon']])

print(df[df['bikescore'] > 100 ][['lat', 'lon']])