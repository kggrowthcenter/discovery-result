from navigation import make_sidebar
import streamlit as st
from data_processing import finalize_data
import pandas as pd

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
    ##### 🔍 1. Mencari Data Peserta  
    - Masukkan **Email/Nama/Nomor Telepon** di kolom pencarian.  
    - Tekan **Enter** untuk menampilkan hasil pencarian.  

    ##### 📊 2. Melihat Hasil Tes  
    - Hasil pencarian berupa Email, Nama, No. Telepon, Tanggal Registrasi, Tanggal Tes, dan Hasil Tes.  
    - Hasil tes dapat diklik untuk melihat detail interpretasi.  

    ##### ⏳ 3. Filter Data Berdasarkan Waktu  
    - Data yang ditampilkan hanya dalam **6 bulan terakhir** secara otomatis.
    - Jika peserta sudah mengerjakan test namun lebih dari 6 bulan tidak akan muncul.  

    📱 Jika ada yang ingin ditanyakan dapat menghubungi WhatsApp 085155012079 (Irsa). 
    """)


df_creds, df_links, df_final = finalize_data()

df_merged = df_final.copy()

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
selected_columns = ["email", "name", "phone", "register_date", "GI_date", "GI_overall"] + list(gi_columns.keys()) + ["LEAN_date"] + list(lean_columns.keys()) + ["ELITE_date"] + list(elite_columns.keys()) + ["Astaka_date", "Astaka_Top 1_typology", "Astaka_Top 1_total_score", "Astaka_Top 2_typology", "Astaka_Top 2_total_score", "Astaka_Top 3_typology", "Astaka_Top 3_total_score", "Astaka_Top 4_typology", "Astaka_Top 4_total_score", "Astaka_Top 5_typology", "Astaka_Top 5_total_score", "Astaka_Top 6_typology", "Astaka_Top 6_total_score"] + ["Genuine_date", "Genuine_Top 1_typology", "Genuine_Top 1_total_score", "Genuine_Top 2_typology", "Genuine_Top 2_total_score", "Genuine_Top 3_typology", "Genuine_Top 3_total_score", "Genuine_Top 4_typology", "Genuine_Top 4_total_score", "Genuine_Top 5_typology", "Genuine_Top 5_total_score", "Genuine_Top 6_typology", "Genuine_Top 6_total_score", "Genuine_Top 7_typology", "Genuine_Top 7_total_score", "Genuine_Top 8_typology", "Genuine_Top 8_total_score", "Genuine_Top 9_typology", "Genuine_Top 9_total_score"]

# --- Search Input ---
search_query = st.text_input("🔍 Search by Email, Name, or Phone", "")

# --- Filter Data Based on Search ---
if search_query:
    df_merged = df_merged[
        df_merged["email"].str.contains(search_query, case=False, na=False) |
        df_merged["name"].str.contains(search_query, case=False, na=False) |
        df_merged["phone"].astype(str).str.contains(search_query, na=False)
    ]
    # --- Display the table only if search input is provided ---
    st.write(f"Showing {len(df_merged)} results")
    st.write(df_merged[selected_columns].head(10).to_html(escape=False, index=False), unsafe_allow_html=True)

else:
    st.write("❗ Enter a search query to see results.")