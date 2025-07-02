import pandas as pd

df = pd.read_csv("DonneesOuvertes2024_010203040506070809101112(1).zip")

df['STARTTIMEDATE'] = pd.to_datetime(df['STARTTIMEMS'], unit = 'ms')

df['month'] = df.STARTTIMEDATE.dt.month

df = df[df['month'] == 1]
df.to_csv('2024_01.csv')