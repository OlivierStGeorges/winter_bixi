import pandas as pd

def add_month_col(df):
    df['STARTTIMEDATE'] = pd.to_datetime(df['STARTTIMEMS'], unit='ms')
    df['month'] = df.STARTTIMEDATE.dt.month
    return df

def generate_winter_dataset(file_jfm, file_dec, output_file):
    # Janv-Fév-Mars
    df = pd.read_csv(file_jfm)
    df = add_month_col(df)
    df = df[df['month'].isin([1, 2, 3])]

    # Décembre de l’année précédente
    df2 = pd.read_csv(file_dec)
    df2 = add_month_col(df2)
    df2 = df2[df2['month'].isin([12])]

    # Concaténer
    df = pd.concat([df2, df], ignore_index=True)

    # Sauvegarder
    df.to_csv(output_file, index=False)

def generate_summer_dataset(csv_in, output_path):
    df = pd.read_csv(csv_in)
    df = add_month_col(df)
    df = df[df['month'].isin([6, 7, 8, 9])]
    df.to_csv(output_path, index=False)


def generate_dataset(season, zip_path, previous_zip_path, output_path):
    if season == "hiver":
        generate_winter_dataset(zip_path, previous_zip_path, output_path)
    elif season == "ete":
        generate_summer_dataset(zip_path, output_path)
    else:
        raise ValueError(f"Saison inconnue : {season}")

