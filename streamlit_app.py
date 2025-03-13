
import streamlit as st
from time import sleep
from navigation import make_sidebar
import streamlit_authenticator as stauth
from data_processing import finalize_data
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    page_title='Discovery Test Result',
    page_icon='🧙‍♂️', 
)

# Fetch the credentials from the data source
df_creds, df_links, df_discovery = finalize_data()

# Process `df_creds` to extract credentials in the required format
def extract_credentials(df_creds):
    credentials = {
        "credentials": {
            "usernames": {}
        },
        "cookie": {
            "name": "growth_center",
            "key": "growth_2024",
            "expiry_days": 30
        }
    }
    for index, row in df_creds.iterrows():
        credentials['credentials']['usernames'][row['username']] = {
            'name': row['name'],  # Add the 'name' field
            'password': row['password'],  # Password should already be hashed
            'unit': row['unit'],  # Store the user's unit for later filtering
            'email': row['email'],  # Add the email field
        }
    return credentials

# Extract credentials from df_creds
credentials = extract_credentials(df_creds)

# Authentication Setup
authenticator = stauth.Authenticate(
    credentials['credentials'],
    credentials['cookie']['name'],
    credentials['cookie']['key'],
    credentials['cookie']['expiry_days'],
    auto_hash=False
)

# Make the sidebar visible only if logged in
if st.session_state.get("logged_in", False):
    make_sidebar()

# Display the title of the app
st.title("🧙‍♂️ Discovery Test Result")

# Display the login form
authenticator.login('main')

# Handle authentication status
if st.session_state.get('authentication_status'):
    st.session_state['logged_in'] = True  # Set session state for logged in
    st.success("Logged in successfully. Go to the Test Result in the sidebar.")
elif st.session_state.get('authentication_status') is False:
    st.error("Incorrect username or password.")
elif st.session_state.get('authentication_status') is None:
    st.warning("Please enter your username and password to log in.")
