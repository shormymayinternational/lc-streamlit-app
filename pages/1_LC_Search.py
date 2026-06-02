import streamlit as st
import pandas as pd
from io import BytesIO

from utils.data_loader import load_data

df = load_data()

st.title("🔍 LC Search")

c1,c2,c3 = st.columns(3)

with c1:

    month_filter = st.selectbox(
        "Month",
        ["All"] +
        sorted(
            df["MONTH_NAME"]
            .unique()
        )
    )

with c2:

    rm_filter = st.selectbox(
        "RM",
        ["All"] +
        sorted(
            df["RM"]
            .astype(str)
            .unique()
        )
    )

with c3:

    bank_filter = st.selectbox(
        "Bank",
        ["All"] +
        sorted(
            df["BANK NAME"]
            .astype(str)
            .unique()
        )
    )

search = st.text_input(
    "Search LC Number / Tracking Number / RM"
)

filtered_df = df.copy()

if month_filter != "All":
    filtered_df = filtered_df[
        filtered_df["MONTH_NAME"]
        == month_filter
    ]

if rm_filter != "All":
    filtered_df = filtered_df[
        filtered_df["RM"]
        == rm_filter
    ]

if bank_filter != "All":
    filtered_df = filtered_df[
        filtered_df["BANK NAME"]
        == bank_filter
    ]

if search:

    mask = False

    for col in filtered_df.columns:

        mask = (
            mask |
            filtered_df[col]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        )

    filtered_df = filtered_df[
        mask
    ]

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=700
)

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="xlsxwriter"
) as writer:

    filtered_df.to_excel(
        writer,
        index=False
    )

st.download_button(
    "Download Results",
    output.getvalue(),
    "LC_Filtered.xlsx"
)