import pandas as pd
import streamlit as st

EXCEL_FILE = r"LC_2026_MT700.xlsx"

@st.cache_data(ttl=300)
def load_data():

    df = pd.read_excel(EXCEL_FILE)

    df.columns = df.columns.str.strip()

    df["DATE"] = pd.to_datetime(
        df["DATE"],
        errors="coerce"
    )

    df["DAY"] = df["DATE"].dt.day

    df["MONTH_NAME"] = (
        df["DATE"]
        .dt.strftime("%B")
    )

    df["CATEGORY"] = (
        df["RM"]
        .fillna("")
        .astype(str)
        .apply(
            lambda x:
            "CPC"
            if "CPC" in x.upper()
            else "NON CPC"
        )
    )

    return df