from navigation import make_sidebar
import streamlit as st
from data_processing import finalize_data
import altair as alt
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title='Demography',
    page_icon=':🌎:', 
)

make_sidebar()
df_survey, df_creds, combined_df = finalize_data()

# FILTER FROM NAVIGATION
columns_list = [
    'unit', 'subunit', 'directorate', 'division','department', 'section',
    'layer', 'status', 'generation', 'gender', 'marital', 'education',
    'tenure_category', 'children', 'region', 'participation_23'
]
def categorize(value):
    if value >= 5:
        return 'High'
    elif value <= 2:
        return 'Low'
    else:
        return None
    
def make_filter(columns_list, df_survey, combined_df):
    # Allow the user to select multiple filter columns (unit, subunit, etc.)
    filter_columns = st.multiselect(
        'Filter the data (optional):',
        options=columns_list,
        format_func=lambda x: x.capitalize()
    )

    # Initialize the filtered data as the original DataFrame
    selected_filters = []
    filtered_data, filtered_combined = df_survey.copy(), combined_df.copy()

    # Display filter options for each selected filter column
    for filter_col in filter_columns:
        selected_filter_value = st.multiselect(
            f'Select {filter_col.capitalize()} to filter the data:',
            options=filtered_data[filter_col].unique(),
            key=f'filter_{filter_col}'
        )
        
        # Check if any values are selected for this filter
        if selected_filter_value:
            # Filter the data to include only rows where the column value is in the selected values
            filtered_data = filtered_data[filtered_data[filter_col].isin(selected_filter_value)]
            filtered_combined = filtered_combined[filtered_combined[filter_col].isin(selected_filter_value)]
            # Add the selected filter values to the list for subheader display
            selected_filters.append(f"{filter_col.capitalize()}: {', '.join(selected_filter_value)}")

    # Confidentiality check: return empty DataFrame if filtered data has only 1 record
    if filtered_data.shape[0] <= 1 or filtered_combined.shape[0] <= 1:
        st.write("Data is unavailable to protect confidentiality.")
        return pd.DataFrame(), pd.DataFrame(), selected_filters

    return filtered_data, filtered_combined, selected_filters

# SESSION STATE
if st.session_state.get('authentication_status'):
    username = st.session_state['username']
    user_units = df_creds.loc[df_creds['username'] == username, 'unit'].values[0].split(', ')
    df_survey = df_survey[df_survey['subunit'].isin(user_units)]
    combined_df = combined_df[combined_df['subunit'].isin(user_units)]
    df_survey['category_sat'] = df_survey['SAT'].apply(categorize)

    st.header('Demography Overview', divider='rainbow')

    high_satisfaction = st.checkbox("Profil Karyawan Puas (Skor 5)")
    low_satisfaction = st.checkbox("Profil Karyawan Tidak Puas (Skor 1 dan 2)")

    if high_satisfaction:
        df_survey = df_survey[df_survey['category_sat'] == 'High']  
        st.subheader('High Satisfaction Demography')
    
    elif low_satisfaction:
        df_survey = df_survey[df_survey['category_sat'] == 'Low'] 
        st.subheader('Low Satisfaction Demography')
    
    else:
        st.subheader('All Demography')

    filtered_data, filtered_combined, selected_filters = make_filter(columns_list, df_survey, combined_df)

    employee = filtered_combined['nik'].nunique()

    col4, col5, col6 = st.columns([1, 1, 1])
    with col4 :
        total_participants = filtered_data['nik'].nunique()
        st.write("Participants")
        st.subheader(total_participants)
    with col5:
        percent_participant = (total_participants / employee) * 100 
        st.write("Overall Participant")
        st.subheader(f"{percent_participant:.1f}%")
    with col6:
        st.write("Total Employee")
        st.subheader(employee)

    st.write("")


    col1, col2, col3 = st.columns(3)
    ######## GENDER ##########
    with col1:
        # Step 1: Capitalize gender values
        filtered_combined['gender'] = filtered_combined['gender'].str.capitalize()

        # Step 2: Calculate Done and Not Done counts by gender
        done_not_done_gender = filtered_combined.groupby('gender').apply(lambda x: pd.Series({
            'Done': x['responden_id'].notnull().sum(),
            'Not Done': x['responden_id'].isnull().sum()
        })).reset_index()

        # Step 3: Melt the DataFrame to use with a 100% stacked bar chart
        done_not_done_gender_melted = done_not_done_gender.melt(id_vars='gender', var_name='Status', value_name='Count')

        # Step 4: Calculate percentages
        done_not_done_gender_melted['Percentage'] = done_not_done_gender_melted.groupby('gender')['Count'].transform(lambda x: x / x.sum() * 100)

        # Step 5: Create the 100% stacked bar chart with custom colors for 'Done' and 'Not Done'
        gender_chart = px.bar(
            done_not_done_gender_melted,
            x='Percentage',
            y='gender',
            color='Status',
            text='Count',
            labels={'gender': 'Gender', 'Percentage': 'Percentage (%)'},
            title="Gender Distribution",
            color_discrete_map={'Done': '#133E87', 'Not Done': '#CBDCEB'}
        )

        # Step 6: Update layout to show both count and percentage
        gender_chart.update_traces(
            texttemplate='%{text} (%{x:.1f}%)', 
            textposition='inside', 
            hovertemplate='Gender: %{y}<br>Count: %{text} (%{x:.1f}%)'
        )
        gender_chart.update_layout(
            barmode='stack', 
            height=200, 
            width=600,
            xaxis_title='Percentage (%)',
            yaxis_title='Gender',
            margin=dict(t=40, b=40, l=0, r=0),
            showlegend=False
        )

        # Display the chart in Streamlit
        st.plotly_chart(gender_chart, use_container_width=True)
    
    ######## GENERATION ############
    with col3 :
        filtered_combined['generation'] = filtered_combined['generation'].str.upper()
        # Step 1: Calculate Done and Not Done counts by generation
        done_not_done_generation = filtered_combined.groupby('generation').apply(lambda x: pd.Series({
            'Done': x['responden_id'].notnull().sum(),
            'Not Done': x['responden_id'].isnull().sum()
        })).reset_index()

        # Step 2: Melt the DataFrame to use with a 100% stacked bar chart
        done_not_done_generation_melted = done_not_done_generation.melt(id_vars='generation', var_name='Status', value_name='Count')

        # Step 3: Calculate percentages
        done_not_done_generation_melted['Percentage'] = done_not_done_generation_melted.groupby('generation')['Count'].transform(lambda x: x / x.sum() * 100)

        # Step 4: Create the 100% stacked bar chart with custom colors for 'Done' and 'Not Done'
        generation_chart = px.bar(
            done_not_done_generation_melted,
            x='Percentage',
            y='generation',
            color='Status',
            text='Count',
            labels={'generation': 'Generation', 'Percentage': 'Percentage (%)'},
            title="Generation Distribution",
            color_discrete_map={'Done': '#133E87', 'Not Done': '#CBDCEB'}
        )

        # Step 5: Update layout to show both count and percentage
        generation_chart.update_traces(
            texttemplate='%{text} (%{x:.1f}%)', 
            textposition='inside', 
            hovertemplate='Generation: %{y}<br>Count: %{text} (%{x:.1f}%)'
        )
        generation_chart.update_layout(
            barmode='stack', 
            height=270, 
            width=600,
            xaxis_title='Percentage (%)',
            yaxis_title='Generation',
            margin=dict(t=40, b=40, l=0, r=0),
            showlegend=False
        )

        # Display the chart in Streamlit
        st.plotly_chart(generation_chart, use_container_width=True)


    ########## EMPLOYEE STATUS #############
    with col2: 
        # Step 1: Calculate Done and Not Done counts by status
        done_not_done_status = filtered_combined.groupby('status').apply(lambda x: pd.Series({
            'Done': x['responden_id'].notnull().sum(),
            'Not Done': x['responden_id'].isnull().sum()
        })).reset_index()

        # Step 2: Melt the DataFrame for a stacked bar chart
        done_not_done_status_melted = done_not_done_status.melt(id_vars='status', var_name='Status', value_name='Count')

        # Step 3: Calculate percentages for the 100% stacked bar chart
        done_not_done_status_melted['Percentage'] = done_not_done_status_melted.groupby('status')['Count'].transform(lambda x: x / x.sum() * 100)

        # Step 4: Create the stacked bar chart with custom colors
        status_chart = px.bar(
            done_not_done_status_melted,
            x='Percentage',
            y='status',
            color='Status',
            text='Count',
            labels={'status': 'Employee Status', 'Percentage': 'Percentage (%)'},
            title="Employee Status Distribution",
            color_discrete_map={'Done': '#133E87', 'Not Done': '#CBDCEB'}  
        )

        # Step 5: Update layout to show both count and percentage
        status_chart.update_traces(
            texttemplate='%{text} (%{x:.1f}%)',
            textposition='inside', 
            hovertemplate='Status: %{y}<br>Count: %{text} (%{x:.1f}%)'
        )
        status_chart.update_layout(
            barmode='stack',
            height=200,
            xaxis_title='Percentage (%)',
            yaxis_title='Employee Status',
            margin=dict(t=40, b=40, l=0, r=0),
            showlegend=False
        )

        # Display the chart in Streamlit
        st.plotly_chart(status_chart, use_container_width=True)

    
    st.write("**Legend:**")
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <div style="width: 18px; height: 18px; background-color: #133E87; margin-right: 10px;"></div>
            <span style="font-size: 14px;">'Done' (Completion)</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 18px; height: 18px; background-color: #CBDCEB; margin-right: 10px;"></div>
            <span style="font-size: 14px;">'Not Done' (Incomplete)</span>
        </div>
        """, unsafe_allow_html=True
    )

    st.divider()


    ######## UNIT ################
    # Step 1: Calculate Done and Not Done counts by unit
    done_not_done = filtered_combined.groupby('unit').apply(lambda x: pd.Series({
        'Done': x['responden_id'].notnull().sum(),
        'Not Done': x['responden_id'].isnull().sum()
    })).reset_index()

    # Step 2: Melt the DataFrame to use with a 100% stacked bar chart
    done_not_done_melted = done_not_done.melt(id_vars='unit', var_name='Status', value_name='Count')

    # Step 3: Calculate percentages
    done_not_done_melted['Percentage'] = done_not_done_melted.groupby('unit')['Count'].transform(lambda x: x / x.sum() * 100)

    # Step 4: Create the 100% stacked bar chart
    fig = px.bar(
        done_not_done_melted,
        y='unit',
        x='Percentage',
        color='Status',
        text='Count',
        labels={'unit': 'Unit', 'Percentage': 'Percentage (%)'},
        title="Unit Distribution by Participation Status",
        color_discrete_map={'Done': '#10375C', 'Not Done': '#D4BDAC'}
    )

    # Step 5: Adjust layout and hover information
    fig.update_traces(
        texttemplate='%{text} (%{x:.1f}%)',  
        textposition='inside', 
        hovertemplate='Unit: %{y}<br>Count: %{text} (%{x:.1f}%)' 
    )
    fig.update_layout(
        barmode='stack', 
        height=500,
        yaxis_title='Unit', 
        xaxis_title='Percentage (%)'
    )
    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    ######## LAYER ################
    layer_mapping = {
        'Group 5 Str Layer 1': 'Director',
        'Group 5': 'Professional setara Director (Consultant)',
        'Group 4 Str Layer 2': 'General Manager',
        'Group 4': 'Professional setara GM (Advisor)',
        'Group 3 Str Layer 3B': 'Senior Manager',
        'Group 3 Str Layer 3A': 'Manager',
        'Group 3': 'Professional setara Manager (Specialist)',
        'Group 2 Str Layer 4': 'Superintendent',
        'Group 2': 'Officer',
        'Group 1 Str Layer 5': 'Team Leader',
        'Group 1': 'Pelaksana',
        '-' :'-'
    }
    df_survey['layer'] = df_survey['layer'].map(layer_mapping)
    combined_df['layer'] = combined_df['layer'].map(layer_mapping)
    filtered_combined['layer'] = filtered_combined['layer'].str.strip()
    layer_order = list(layer_mapping.values())
    layer_dtype = pd.CategoricalDtype(categories=layer_order, ordered=True)
    filtered_combined['layer'] = filtered_combined['layer'].astype(layer_dtype)
    filtered_combined['layer'] = filtered_combined['layer'].str.strip()
    
    # Step 1: Calculate Done and Not Done counts by layer
    done_not_done_layer = filtered_combined.groupby('layer').apply(lambda x: pd.Series({
        'Done': x['responden_id'].notnull().sum(),
        'Not Done': x['responden_id'].isnull().sum()
    })).reset_index()
   
    # Hapus layer yang tidak ada data sama sekali
    done_not_done_layer = done_not_done_layer[
        (done_not_done_layer['Done'] > 0) | (done_not_done_layer['Not Done'] > 0)
    ]
    
    # Filter layer_order sesuai dengan layer yang ada di data
    available_layers = done_not_done_layer['layer'].unique()
    layer_order_filtered = [layer for layer in layer_order if layer in available_layers]
    
    # Melt DataFrame untuk grafik
    done_not_done_layer_melted = done_not_done_layer.melt(id_vars='layer', var_name='Status', value_name='Count')
    
    done_not_done_layer_melted['layer'] = pd.Categorical(
        done_not_done_layer_melted['layer'],
        categories=layer_order_filtered,
        ordered=True
    )
    
    # Hitung persentase
    done_not_done_layer_melted['Percentage'] = done_not_done_layer_melted.groupby('layer')['Count'].transform(lambda x: x / x.sum() * 100)
    
    # Buat grafik
    layer_chart = px.bar(
        done_not_done_layer_melted,
        y='layer',
        x='Percentage',
        color='Status',
        text='Count',
        labels={'layer': 'Layer', 'Percentage': 'Percentage (%)'},
        title="Layer Distribution by Participation Status",
        color_discrete_map={'Done': '#10375C', 'Not Done': '#D4BDAC'}
    )
    
    # Perbarui urutan layer di grafik
    layer_chart.update_yaxes(categoryorder='array', categoryarray=layer_order_filtered)
    
    # Perbarui tampilan grafik
    layer_chart.update_traces(
        texttemplate='%{text} (%{x:.1f}%)', 
        textposition='inside', 
        hovertemplate='Layer: %{y}<br>Count: %{text} (%{x:.1f}%)'
    )
    layer_chart.update_layout(
        barmode='stack', 
        height=400,
        width=600,
        yaxis_title='Layer', 
        xaxis_title='Percentage (%)',
        coloraxis_showscale=False,  
        margin=dict(t=30, b=40, l=20, r=0)
    )
    
    # Tampilkan grafik di Streamlit
    st.plotly_chart(layer_chart, use_container_width=True)


    #################TENURE###################
    # Step 1: Calculate Done and Not Done counts by tenure_category
    done_not_done_tenure = filtered_combined.groupby('tenure_category').apply(lambda x: pd.Series({
        'Done': x['responden_id'].notnull().sum(),
        'Not Done': x['responden_id'].isnull().sum()
    })).reset_index()

    # Step 2: Melt the DataFrame to use with a 100% stacked bar chart
    done_not_done_tenure_melted = done_not_done_tenure.melt(id_vars='tenure_category', var_name='Status', value_name='Count')

    # Step 3: Calculate percentages
    done_not_done_tenure_melted['Percentage'] = done_not_done_tenure_melted.groupby('tenure_category')['Count'].transform(lambda x: x / x.sum() * 100)
    done_not_done_tenure_melted = done_not_done_tenure_melted.sort_values(by='tenure_category', ascending=False)

    # Step 4: Create the horizontal 100% stacked bar chart
    tenure_chart = px.bar(
        done_not_done_tenure_melted,
        x='Percentage',
        y='tenure_category',
        color='Status',
        text='Count',
        labels={'tenure_category': 'Tenure Category', 'Percentage': 'Percentage (%)'},
        title="Tenure Distribution by Participation Status",
        color_discrete_map={'Done': '#10375C', 'Not Done': '#D4BDAC'}
    )

    # Step 5: Update layout to show both count and percentage
    tenure_chart.update_traces(
        texttemplate='%{text} (%{x:.1f}%)', 
        textposition='inside', 
        hovertemplate='Tenure: %{y}<br>Count: %{text} (%{x:.1f}%)'
    )
    tenure_chart.update_layout(
        barmode='stack', 
        height=300, 
        width=600,
        xaxis_title='Percentage (%)',
        yaxis_title='Tenure',
        coloraxis_showscale=False, 
        margin=dict(t=20, b=40, l=50, r=0)
    )

    # Display the chart in Streamlit
    st.plotly_chart(tenure_chart, use_container_width=True)
    st.divider()

    # New Select Box for additional demographic data
    st.write("Additional Demographic Distribution")
    selected_demo_category = st.selectbox(
        "Select Demographic Category:",
        options=['subunit', 'directorate', 'division', 'department', 'section',
        'marital', 'education',
        'children', 'region', 'participation_23']
    )

    # Step 1: Group by selected demographic category and calculate Done/Not Done
    demo_done_not_done = filtered_combined.groupby(selected_demo_category).apply(lambda x: pd.Series({
        'Done': x['responden_id'].notnull().sum(),
        'Not Done': x['responden_id'].isnull().sum()
    })).reset_index()

    # Step 2: Melt the DataFrame to prepare for a stacked bar chart
    demo_done_not_done_melted = demo_done_not_done.melt(
        id_vars=selected_demo_category, 
        var_name='Status', 
        value_name='Count'
    )

    # Step 3: Calculate percentages
    demo_done_not_done_melted['Percentage'] = demo_done_not_done_melted.groupby(selected_demo_category)['Count'].transform(lambda x: x / x.sum() * 100)

    # Step 4: Create horizontal stacked bar chart
    fig = px.bar(
        demo_done_not_done_melted,
        x='Percentage',
        y=selected_demo_category,
        color='Status',
        text='Count',
        labels={
            selected_demo_category: selected_demo_category.capitalize(),
            'Percentage': 'Percentage (%)',
            'Status': 'Completion Status'
        },
        title=f"{selected_demo_category.capitalize()} Distribution by Completion Status",
        color_discrete_map={'Done': '#4682B4', 'Not Done': '#B0C4DE'}  # Customize colors
    )

    # Step 5: Update layout and text labels
    fig.update_traces(
        texttemplate='%{text} (%{x:.1f}%)',  # Show count and percentage
        textposition='inside'
    )

    fig.update_layout(
        barmode='stack',  # Stacked 100% bar chart
        height=800,
        width=800,
        xaxis_title='Percentage (%)',
        yaxis_title=selected_demo_category.capitalize()
    )

    # Display chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
