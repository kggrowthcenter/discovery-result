from fetch_data import fetch_data_creds, fetch_data_discovery
import pandas as pd
import streamlit as st

def process_astaka(df):
    # Filter only Astaka bundle
    df_astaka = df[df["bundle_name"] == "Astaka"].copy()

    # Sort by id, latest taken_date first, highest score first
    df_astaka = df_astaka.sort_values(by=["id", "taken_date", "total_score"], ascending=[True, False, False])

    # Rank the results per user (Top 1 - Top 6)
    df_astaka["rank"] = df_astaka.groupby("id").cumcount() + 1

    # Keep only Top 6 results
    df_astaka = df_astaka[df_astaka["rank"] <= 6]

    # Pivot to have columns like "Astaka_Top 1_Typology", "Astaka_Top 2_Score"
    df_astaka_pivot = df_astaka.pivot(index=["id", "email", "name", "phone", "register_date"],
                                      columns="rank",
                                      values=["typology", "total_score"]).reset_index()

    # Rename columns properly
    df_astaka_pivot.columns = [
        f"Astaka_Top {col[1]}_{col[0]}" if isinstance(col, tuple) and col[1] else col[0]
        for col in df_astaka_pivot.columns
    ]

    # Process taken date separately (only latest one)
    df_astaka_date = df_astaka.groupby(["id", "email", "name", "phone", "register_date"])["taken_date"].max().reset_index()
    df_astaka_date.rename(columns={"taken_date": "Astaka_date"}, inplace=True)

    # Merge both typology + score and latest taken_date
    df_astaka_final = df_astaka_pivot.merge(df_astaka_date, on=["id", "email", "name", "phone", "register_date"], how="left")

    return df_astaka_final

def process_genuine(df):
    # Filter only Genuine bundle
    df_genuine = df[df["bundle_name"] == "Genuine"].copy()

    # Sort by id, latest taken_date first, highest score first
    df_genuine = df_genuine.sort_values(by=["id", "taken_date", "total_score"], ascending=[True, False, False])

    # Rank the results per user (Top 1 - Top 9)
    df_genuine["rank"] = df_genuine.groupby("id").cumcount() + 1

    # Keep only Top 9 results
    df_genuine = df_genuine[df_genuine["rank"] <= 9]

    # Pivot to create columns like "Genuine_Top 1_Typology", "Genuine_Top 2_Score"
    df_genuine_pivot = df_genuine.pivot(index=["id", "email", "name", "phone", "register_date"],
                                        columns="rank",
                                        values=["typology", "total_score"]).reset_index()

    # Rename columns properly
    df_genuine_pivot.columns = [
        f"Genuine_Top {col[1]}_{col[0]}" if isinstance(col, tuple) and col[1] else col[0]
        for col in df_genuine_pivot.columns
    ]

    # Process taken date separately (only latest one)
    df_genuine_date = df_genuine.groupby(["id", "email", "name", "phone", "register_date"])["taken_date"].max().reset_index()
    df_genuine_date.rename(columns={"taken_date": "Genuine_date"}, inplace=True)

    # Merge both typology + score and latest taken_date
    df_genuine_final = df_genuine_pivot.merge(df_genuine_date, on=["id", "email", "name", "phone", "register_date"], how="left")

    return df_genuine_final

# --- Function to Transform Data ---
def process_others(df):
    # Define the bundle names to process
    bundle_names = ["GI", "LEAN", "ELITE"]
    df_list = []

    for bundle in bundle_names:
        # Filter data for the current bundle_name
        df_bundle = df[df["bundle_name"] == bundle]

        # Pivot final_result separately
        df_final_result = df_bundle.pivot_table(
            index=["id", "email", "name", "phone", "register_date"],
            values="final_result",
            aggfunc="first"
        ).reset_index()
        df_final_result.rename(columns={"final_result": f"{bundle}_overall"}, inplace=True)

        # Pivot typology with test_name for the current bundle
        df_typology = df_bundle.pivot_table(
            index=["id", "email", "name", "phone", "register_date"],
            columns=["test_name"],
            values="typology",
            aggfunc="first"
        )

        # Pivot taken_date for the current bundle (without test_name)
        df_taken_date = df_bundle.pivot_table(
            index=["id", "email", "name", "phone", "register_date"],
            values="taken_date",
            aggfunc="first"
        ).reset_index()
        df_taken_date.rename(columns={"taken_date": f"{bundle}_date"}, inplace=True)

        # Rename typology columns for clarity
        df_typology.columns = [f"{bundle}_{col}" for col in df_typology.columns]
        df_typology = df_typology.reset_index()

        # Merge final_result, taken_date, and typology
        df_bundle_pivot = df_final_result.merge(df_taken_date, on=["id", "email", "name", "phone", "register_date"], how="left")
        df_bundle_pivot = df_bundle_pivot.merge(df_typology, on=["id", "email", "name", "phone", "register_date"], how="left")

        df_list.append(df_bundle_pivot)

    # Merge all bundle pivots using an outer join
    if df_list:
        df_final = df_list[0]
        for df_bundle_pivot in df_list[1:]:
            df_final = df_final.merge(df_bundle_pivot, on=["id", "email", "name", "phone", "register_date"], how="outer")
    else:
        df_final = pd.DataFrame()  # Handle empty case

    return df_final

def finalize_data():
    df_creds, df_links = fetch_data_creds()
    df_discovery = fetch_data_discovery()

    # Trim spaces in specific columns
    df_links["Tipologi"] = df_links["Tipologi"].str.strip()
    df_discovery["typology"] = df_discovery["typology"].str.strip()
    df_discovery["final_result"] = df_discovery["final_result"].str.strip()

    # Load and process the data
    df_others = process_others(df_discovery)
    df_astaka = process_astaka(df_discovery)
    df_genuine = process_genuine(df_discovery)

    # Start merging with df_others as the base
    df_final = df_others.merge(df_astaka, on=["id", "email", "name", "phone", "register_date"], how="left")
    df_final = df_final.merge(df_genuine, on=["id", "email", "name", "phone", "register_date"], how="left")

    # Define the expected column order
    column_order = [
        "id", "email", "name", "phone", "register_date",
        "GI_date", "GI_overall", "GI_Creativity Style", "GI_Curiosity", "GI_Grit", "GI_Humility",
        "GI_Meaning Making", "GI_Mindset", "GI_Purpose in Life",
        "LEAN_date", "LEAN_overall", "LEAN_Cognitive Flexibility", "LEAN_Intellectual Curiosity", "LEAN_Open-Mindedness",
        "LEAN_Personal Learner", "LEAN_Self-Reflection", "LEAN_Self-Regulation", "LEAN_Social Astuteness",
        "LEAN_Social Flexibility", "LEAN_Unconventional Thinking",
        "ELITE_date", "ELITE_overall", "ELITE_Empathy", "ELITE_Motivation", "ELITE_Self-Awareness",
        "ELITE_Self-Regulation", "ELITE_Social skills",
        "Astaka_date", "Astaka_Top 1_typology", "Astaka_Top 1_total_score", "Astaka_Top 2_typology",
        "Astaka_Top 2_total_score", "Astaka_Top 3_typology", "Astaka_Top 3_total_score",
        "Astaka_Top 4_typology", "Astaka_Top 4_total_score", "Astaka_Top 5_typology",
        "Astaka_Top 5_total_score", "Astaka_Top 6_typology", "Astaka_Top 6_total_score",
        "Genuine_date", "Genuine_Top 1_typology", "Genuine_Top 1_total_score", "Genuine_Top 2_typology",
        "Genuine_Top 2_total_score", "Genuine_Top 3_typology", "Genuine_Top 3_total_score",
        "Genuine_Top 4_typology", "Genuine_Top 4_total_score", "Genuine_Top 5_typology",
        "Genuine_Top 5_total_score", "Genuine_Top 6_typology", "Genuine_Top 6_total_score",
        "Genuine_Top 7_typology", "Genuine_Top 7_total_score", "Genuine_Top 8_typology",
        "Genuine_Top 8_total_score", "Genuine_Top 9_typology", "Genuine_Top 9_total_score"
    ]

    # Reorder columns (keep only the ones that exist in the DataFrame)
    df_final = df_final[[col for col in column_order if col in df_final.columns]]

    return df_creds, df_links, df_final