import pandas as pd

def add_month_col(df):
    df['STARTTIMEDATE'] = pd.to_datetime(df['STARTTIMEMS'], unit='ms')

    df['month'] = df.STARTTIMEDATE.dt.month
    return df

df = pd.read_csv("DonneesOuvertes2024_010203040506070809101112(1).zip")

df = add_month_col(df)

df = df[df['month'].isin([1,2,3])]


df2 = pd.read_csv("DonneesOuvertes2023_12.zip")

df2 = add_month_col(df2)

df2 = df2[df2['month'].isin([12])]

df = pd.concat([df2, df2], ignore_index=True)

df.to_csv('hiver_2023_2024.csv')