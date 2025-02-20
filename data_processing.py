from fetch_data import fetch_data_creds, fetch_data_discovery

def finalize_data():
    df_creds = fetch_data_creds()
    df_discovery = fetch_data_discovery()

    return df_creds, df_discovery