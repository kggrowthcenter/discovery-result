import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
import pandas as pd


def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]


def make_sidebar():
    with st.sidebar:
        st.title("Sidebar")
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            st.page_link("pages/page1.py", label="Test Result", icon="🎭")

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "streamlit_app":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("streamlit_app.py")


def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("streamlit_app.py")

def make_filter(columns_list, dataframe):
    # Allow the user to select multiple filter columns (unit, subunit, etc.)
    filter_columns = st.multiselect(
        'Filter the data (optional):',
        options=columns_list,
        format_func=lambda x: x.capitalize()
    )

    # Initialize the filtered data as the original DataFrame
    filtered_data = dataframe.copy()

    # List to store selected filter values for display in the subheader
    selected_filters = []

    # Display filter options for each selected filter column
    for filter_col in filter_columns:
        selected_filter_value = st.multiselect(
            f'Select {filter_col.capitalize()} to filter the data:',
            options=filtered_data[filter_col].unique(),
            key=f'filter_{filter_col}'  # Unique key for each filter selectbox
        )
        
        # Check if any values are selected for this filter
        if selected_filter_value:
            # Filter the data to include only rows where the column value is in the selected values
            filtered_data = filtered_data[filtered_data[filter_col].isin(selected_filter_value)]
            
            # Add the selected filter values to the list for subheader display
            selected_filters.append(f"{filter_col.capitalize()}: {', '.join(selected_filter_value)}")
    
    return filtered_data, selected_filters
