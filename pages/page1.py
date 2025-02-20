from navigation import make_sidebar
import streamlit as st
from data_processing import finalize_data
import altair as alt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title='Test Result',
    page_icon=':🎭:', 
)

make_sidebar()
df_creds, df_discovery = finalize_data()

st.write(df_discovery.head())
