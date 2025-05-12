from navigation import make_sidebar
import streamlit as st
from data_processing import finalize_data
import pandas as pd
import base64
import re
from datetime import datetime
import io
import xlsxwriter
from datetime import timedelta

st.set_page_config(
    page_title='Test Result',
    page_icon=':🎭:', 
)

make_sidebar()

# Display the title of the app
st.title("🧙‍♂️ Discovery Test Result")

import streamlit as st  

with st.expander("📌 **Instruksi Penggunaan**"):
    st.markdown(""" 
    ##### ⏳ 1. Filter Data Berdasarkan Waktu  
    - Data yang ditampilkan hanya dalam **6 bulan terakhir** secara otomatis.
    - Jika peserta sudah mengerjakan test namun lebih dari 6 bulan tidak akan muncul.
    - Masukan rentang tanggal untuk melihat hasil dari periode tertentu atau klik tombol "Bulan Ini" 
                 
    ##### 🔍 2. Mencari Data Peserta  
    - Masukkan **Voucher/Email/Nama/Nomor Telepon** di kolom pencarian.  
    - Tekan **Enter** untuk menampilkan hasil pencarian.  

    ##### 📊 3. Melihat Hasil Tes  
    - Hasil pencarian berupa Email, Nama, No. Telepon, Tanggal Registrasi, Tanggal Tes, dan Hasil Tes.  
    - Hasil tes dapat diklik untuk melihat detail interpretasi.  

    📱 Jika ada yang ingin ditanyakan dapat menghubungi WhatsApp 085155012079 (Irsa). 
    """)


df_creds, df_links, df_final = finalize_data()

# --- Calculate global min/max for all *_date columns ---
date_columns = [col for col in df_final.columns if col.endswith("_date") and col != "register_date"]
min_date = pd.to_datetime(df_final[date_columns].min().min())
max_date = pd.to_datetime(df_final[date_columns].max().max())

# Initialize session state for date filters if not already set
if 'start_date' not in st.session_state:
    today = datetime.today()
    st.session_state.start_date = today.replace(day=1)  # Default to the start of the current month
    st.session_state.end_date = min(today.replace(day=1) + pd.DateOffset(months=1) - pd.Timedelta(days=1), datetime.today())

# --- UI for date range and button ---
st.subheader("📆 Date Range")

# Set default values to full range
start_date_default = min_date
end_date_default = max_date

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Bulan Ini"):
        today = datetime.today()
        st.session_state.start_date = pd.to_datetime(today.replace(day=1))
        last_day_of_month = (today.replace(day=1) + pd.DateOffset(months=1)) - pd.Timedelta(days=1)
        st.session_state.end_date = min(pd.to_datetime(last_day_of_month), datetime.today())

with col2:
    if st.button("Minggu Ini"):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())  # Senin
        end_of_week = start_of_week + timedelta(days=6)  # Minggu
        st.session_state.start_date = pd.to_datetime(start_of_week)
        st.session_state.end_date = min(pd.to_datetime(end_of_week), datetime.today())

with col3:
    if st.button("Minggu Kemarin"):
        today = datetime.today()
        start_of_this_week = today - timedelta(days=today.weekday())
        start_of_last_week = start_of_this_week - timedelta(days=7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        st.session_state.start_date = pd.to_datetime(start_of_last_week)
        st.session_state.end_date = min(pd.to_datetime(end_of_last_week), datetime.today())

with col4:
    if st.button("6 Bulan"):
        # For the last 6 months, we can simply use min_date and max_date from the data
        six_months_ago = max_date - pd.DateOffset(months=6)
        st.session_state.start_date = six_months_ago
        st.session_state.end_date = max_date

# Date range input using session state
start_date, end_date = st.date_input(
    "Select date range:",
    value=(st.session_state.start_date, st.session_state.end_date),
    min_value=datetime(2020, 1, 1),  # Assuming data starts from 2020
    max_value=datetime.today()
)

# Convert to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Save the selected date range back to session state
st.session_state.start_date = pd.to_datetime(start_date)
st.session_state.end_date = pd.to_datetime(end_date)

# Process each test block separately
df_filtered = df_final.copy()

for date_col in date_columns:
    # Check which rows are outside the selected date range
    out_of_range = ~((df_filtered[date_col] >= start_date) & (df_filtered[date_col] <= end_date))

    # Get the test prefix, e.g., GI, LEAN, etc.
    test_prefix = date_col.replace("_date", "")

    # Find all columns belonging to this test (except date)
    test_columns = [col for col in df_final.columns if col.startswith(test_prefix + "_") and col != date_col]

    # Set both test columns and the date column to NaN if out of range
    df_filtered.loc[out_of_range, test_columns + [date_col]] = None

# Identify only the test-related columns (exclude identity columns)
identity_columns = ["voucher", "id", "email", "name", "phone", "register_date"]
test_columns_only = [col for col in df_filtered.columns if col not in identity_columns]

# Drop rows where all test-related columns are NaN
df_filtered = df_filtered.dropna(subset=test_columns_only, how='all')


df_merged = df_filtered.copy()

# GI

# Daftar kolom yang akan di-hyperlink
gi_columns = {
    "GI_Creativity Style": "GI_Creativity Style",
    "GI_Curiosity": "GI_Curiosity",
    "GI_Grit": "GI_Grit",
    "GI_Humility": "GI_Humility",
    "GI_Meaning Making": "GI_Meaning Making",
    "GI_Mindset": "GI_Mindset",
    "GI_Purpose in life": "GI_Purpose in Life"
}

# Loop untuk merge & buat hyperlink
for new_col, merge_col in gi_columns.items():
    df_merged = df_merged.merge(
        df_links, left_on=merge_col, right_on="Tipologi", how="left", 
        suffixes=("", f"_{new_col}")  # Tambahkan suffix sesuai GI yang diproses
    )

    # Cari kolom yang sesuai dengan suffix
    link_col = f"Link_{new_col}" if f"Link_{new_col}" in df_merged.columns else "Link"
    tipologi_col = f"Tipologi_{new_col}" if f"Tipologi_{new_col}" in df_merged.columns else "Tipologi"

    # Buat hyperlink
    df_merged[new_col] = df_merged.apply(
        lambda row: f'<a href="{row[link_col]}" target="_blank">{row[tipologi_col]}</a>' 
        if pd.notna(row[link_col]) else row[tipologi_col], 
        axis=1
    )

# LEAN

# Daftar kolom yang akan di-hyperlink
lean_columns = {
    "LEAN_overall": "LEAN_overall",
    "LEAN_Cognitive Felxibility": "LEAN_Cognitive Flexibility",
    "LEAN_Intellectual Curiosity": "LEAN_Intellectual Curiosity",
    "LEAN_Open-Mindedness": "LEAN_Open-Mindedness",
    "LEAN_Personal Learner": "LEAN_Personal Learner",
    "LEAN_Self-Reflection": "LEAN_Self-Reflection",
    "LEAN_Self-Regulation": "LEAN_Self-Regulation",
    "LEAN_Social Astuteness": "LEAN_Social Astuteness",
    "LEAN_Social Flexibility": "LEAN_Social Flexibility",
    "LEAN_Unconventional Thinking": "LEAN_Unconventional Thinking"
}

# Loop untuk merge & buat hyperlink
for new_col, merge_col in lean_columns.items():
    df_merged = df_merged.merge(
        df_links, left_on=merge_col, right_on="Tipologi", how="left", 
        suffixes=("", f"_{new_col}")  # Tambahkan suffix sesuai GI yang diproses
    )

    # Cari kolom yang sesuai dengan suffix
    link_col = f"Link_{new_col}" if f"Link_{new_col}" in df_merged.columns else "Link"
    tipologi_col = f"Tipologi_{new_col}" if f"Tipologi_{new_col}" in df_merged.columns else "Tipologi"

    # Buat hyperlink
    df_merged[new_col] = df_merged.apply(
        lambda row: f'<a href="{row[link_col]}" target="_blank">{row[tipologi_col]}</a>' 
        if pd.notna(row[link_col]) else row[tipologi_col], 
        axis=1
    )

# ELITE

# Daftar kolom yang akan di-hyperlink
elite_columns = {
    "ELITE_overall": "ELITE_overall",
    "ELITE_Empathy": "ELITE_Empathy",
    "ELITE_Motivation": "ELITE_Motivation",
    "ELITE_Self-Awareness": "ELITE_Self-Awareness",
    "ELITE_Self-Regulation": "ELITE_Self-Regulation",
    "ELITE_Social skills": "ELITE_Social skills"
}

# Loop untuk merge & buat hyperlink
for new_col, merge_col in elite_columns.items():
    df_merged = df_merged.merge(
        df_links, left_on=merge_col, right_on="Tipologi", how="left", 
        suffixes=("", f"_{new_col}")  # Tambahkan suffix sesuai GI yang diproses
    )

    # Cari kolom yang sesuai dengan suffix
    link_col = f"Link_{new_col}" if f"Link_{new_col}" in df_merged.columns else "Link"
    tipologi_col = f"Tipologi_{new_col}" if f"Tipologi_{new_col}" in df_merged.columns else "Tipologi"

    # Buat hyperlink
    df_merged[new_col] = df_merged.apply(
        lambda row: f'<a href="{row[link_col]}" target="_blank">{row[tipologi_col]}</a>' 
        if pd.notna(row[link_col]) else row[tipologi_col], 
        axis=1
    )

# Astaka

# Daftar kolom yang akan di-hyperlink
astaka_columns = {
    "Astaka_Top 1_typology": "Astaka_Top 1_typology",
    "Astaka_Top 2_typology": "Astaka_Top 2_typology",
    "Astaka_Top 3_typology": "Astaka_Top 3_typology",
    "Astaka_Top 4_typology": "Astaka_Top 4_typology",
    "Astaka_Top 5_typology": "Astaka_Top 5_typology",
    "Astaka_Top 6_typology": "Astaka_Top 6_typology"
}

# Loop untuk merge & buat hyperlink
for new_col, merge_col in astaka_columns.items():
    df_merged = df_merged.merge(
        df_links, left_on=merge_col, right_on="Tipologi", how="left", 
        suffixes=("", f"_{new_col}")  # Tambahkan suffix sesuai GI yang diproses
    )

    # Cari kolom yang sesuai dengan suffix
    link_col = f"Link_{new_col}" if f"Link_{new_col}" in df_merged.columns else "Link"
    tipologi_col = f"Tipologi_{new_col}" if f"Tipologi_{new_col}" in df_merged.columns else "Tipologi"

    # Buat hyperlink
    df_merged[new_col] = df_merged.apply(
        lambda row: f'<a href="{row[link_col]}" target="_blank">{row[tipologi_col]}</a>' 
        if pd.notna(row[link_col]) else row[tipologi_col], 
        axis=1
    )

# Genuine

# Daftar kolom yang akan di-hyperlink
genuine_columns = {
"Genuine_Top 1_typology": "Genuine_Top 1_typology",
"Genuine_Top 2_typology": "Genuine_Top 2_typology",
"Genuine_Top 3_typology": "Genuine_Top 3_typology",
"Genuine_Top 4_typology": "Genuine_Top 4_typology",
"Genuine_Top 5_typology": "Genuine_Top 5_typology",
"Genuine_Top 6_typology": "Genuine_Top 6_typology",
"Genuine_Top 7_typology": "Genuine_Top 7_typology",
"Genuine_Top 8_typology": "Genuine_Top 8_typology",
"Genuine_Top 9_typology": "Genuine_Top 9_typology"
}

# Loop untuk merge & buat hyperlink
for new_col, merge_col in genuine_columns.items():
    df_merged = df_merged.merge(
        df_links, left_on=merge_col, right_on="Tipologi", how="left", 
        suffixes=("", f"_{new_col}")  # Tambahkan suffix sesuai GI yang diproses
    )

    # Cari kolom yang sesuai dengan suffix
    link_col = f"Link_{new_col}" if f"Link_{new_col}" in df_merged.columns else "Link"
    tipologi_col = f"Tipologi_{new_col}" if f"Tipologi_{new_col}" in df_merged.columns else "Tipologi"

    # Buat hyperlink
    df_merged[new_col] = df_merged.apply(
        lambda row: f'<a href="{row[link_col]}" target="_blank">{row[tipologi_col]}</a>' 
        if pd.notna(row[link_col]) else row[tipologi_col], 
        axis=1
    )

# --- Display Data ---

# Pilih kolom yang ingin ditampilkan
selected_columns = ["voucher", "email", "name", "phone", "register_date", "GI_date", "GI_overall"] + list(gi_columns.keys()) + ["LEAN_date"] + list(lean_columns.keys()) + ["ELITE_date"] + list(elite_columns.keys()) + ["Astaka_date", "Astaka_Top 1_typology", "Astaka_Top 1_total_score", "Astaka_Top 2_typology", "Astaka_Top 2_total_score", "Astaka_Top 3_typology", "Astaka_Top 3_total_score", "Astaka_Top 4_typology", "Astaka_Top 4_total_score", "Astaka_Top 5_typology", "Astaka_Top 5_total_score", "Astaka_Top 6_typology", "Astaka_Top 6_total_score"] + ["Genuine_date", "Genuine_Top 1_typology", "Genuine_Top 1_total_score", "Genuine_Top 2_typology", "Genuine_Top 2_total_score", "Genuine_Top 3_typology", "Genuine_Top 3_total_score", "Genuine_Top 4_typology", "Genuine_Top 4_total_score", "Genuine_Top 5_typology", "Genuine_Top 5_total_score", "Genuine_Top 6_typology", "Genuine_Top 6_total_score", "Genuine_Top 7_typology", "Genuine_Top 7_total_score", "Genuine_Top 8_typology", "Genuine_Top 8_total_score", "Genuine_Top 9_typology", "Genuine_Top 9_total_score"]

# --- Utility: Generate Download Link ---
def get_table_download_link(df, filename="search_template.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download search template (CSV)</a>'
    return href

st.subheader("🔍 Search Options")

search_query = st.text_input("Search by Voucher, Email, Name, or Phone (you can enter multiple, separated by commas)", "")

with st.expander("Mencari dengan Daftar Peserta"):
    uploaded_file = st.file_uploader("Upload a file (.csv or .xlsx) with a column: email, name, or phone", type=["csv", "xlsx"])

    # --- Provide Search Template ---
    template_df = pd.DataFrame({
        "email": ["example1@email.com", "example2@email.com"],
        "name": ["John Doe", "Jane Smith"],
        "phone": ["081234567890", "089876543210"]
    })
    st.markdown(get_table_download_link(template_df), unsafe_allow_html=True)

search_values = set()

# Process uploaded file
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        file_df = pd.read_csv(uploaded_file)
    else:
        file_df = pd.read_excel(uploaded_file)
    
    for col in ['voucher', 'email', 'name', 'phone']:
        if col in file_df.columns:
            search_values.update(file_df[col].dropna().astype(str).str.strip().str.lower())

# Add single input to the set
if search_query:
    queries = [q.strip().lower() for q in search_query.split(",") if q.strip()]
    search_values.update(queries)

# Filter if any search input exists
if search_values:
    pattern = '|'.join([re.escape(val) for val in search_values if val])  # safely join values as regex pattern
    df_merged_filtered = df_merged[
        df_merged["voucher"].str.lower().str.contains(pattern, na=False) |
        df_merged["email"].str.lower().str.contains(pattern, na=False) |
        df_merged["name"].str.lower().str.contains(pattern, na=False) |
        df_merged["phone"].astype(str).str.lower().str.contains(pattern, na=False)
    ]
    st.write(f"Showing {len(df_merged_filtered)} results")

    # Create a buffer to hold the Excel file
    excel_buffer = io.BytesIO()

    # Prepare the Excel export
    def extract_hyperlink(text):
        if isinstance(text, str) and text.startswith('<a href="'):
            start = text.find('href="') + 6
            end = text.find('"', start)
            url = text[start:end]
            
            start_text = text.find('>') + 1
            end_text = text.rfind('</a>')
            display_text = text[start_text:end_text]
            
            return url, display_text
        return None, None

    # Prepare the Excel export
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df_for_excel = df_merged_filtered[selected_columns].copy()  # Create a copy of the cleaned DataFrame
        df_for_excel.to_excel(writer, index=False, sheet_name='Test Results')  # Write the DataFrame to Excel
        
        # Access the xlsxwriter workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Test Results']
        
        # Loop through each column and set hyperlinks
        for col_num, column in enumerate(df_for_excel.columns):
            for row_num, value in enumerate(df_for_excel[column]):
                url, display_text = extract_hyperlink(value)
                if url:
                    # Set the hyperlink in the cell if it contains a valid URL
                    worksheet.write_url(row_num + 1, col_num, url, string=display_text)
                    
    # Set the file pointer to the beginning of the buffer
    excel_buffer.seek(0)

    # Offer the file as a download link
    st.download_button(
        label="Download Test Results as Excel",
        data=excel_buffer,
        file_name="test_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.write(df_merged_filtered[selected_columns].to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.write("❗ Enter a search query or upload a file to see results.")

