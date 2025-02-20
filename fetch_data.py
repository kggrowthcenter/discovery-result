import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import toml
import pymysql


@st.cache_resource()
def fetch_data_creds():
    secret_info = st.secrets["sheets"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secret_info, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open('Discovery Test Result - Dashboard Credentials')
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()
    df_creds = pd.DataFrame(data)
    return df_creds

@st.cache_resource(ttl=43200)
def fetch_data_discovery():
    try:
        connection_kwargs = {
            'host': st.secrets["discovery"]["host"],
            'port': st.secrets["discovery"]["port"],
            'user': st.secrets["discovery"]["user"],
            'password': st.secrets["discovery"]["password"],
            'database': st.secrets["discovery"]["database"],
            'cursorclass': pymysql.cursors.DictCursor,
        }
        conn = pymysql.connect(**connection_kwargs)

        with open('query_discovery.sql', 'r') as sql_file:
            query = sql_file.read()

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"An error occurred while fetching data from Discovery: {e}")
        return pd.DataFrame()
