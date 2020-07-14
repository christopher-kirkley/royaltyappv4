import pandas

def clean_df(df):
    df['track_artist'] = df['track_artist'].str.replace("’", "'")
    df['track_artist'] = df['track_artist'].str.title()
    df['catalog_artist'] = df['catalog_artist'].str.replace("’", "'")
    df['catalog_artist'] = df['catalog_artist'].str.title()
    return df

    
