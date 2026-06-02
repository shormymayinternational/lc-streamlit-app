import streamlit as st
import pandas as pd
import tempfile

from utils.data_loader import load_data
from utils.charts import branch_heatmap
from utils.pdf_report import generate_pdf

# =========================
# LOAD DATA
# =========================
df = load_data()

st.title("📊 Monthly Analysis")

# =========================
# SAFE CHECK
# =========================
required_cols = [
    "MONTH_NAME",
    "BANK NAME",
    "DAY",
    "LC Number",
    "BRANCH",
    "RM",
    "Tracking Number"
]

missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.error(f"Missing columns in dataset: {missing_cols}")
    st.stop()

# =========================
# CLEAN DATA
# =========================
df = df.dropna(subset=["MONTH_NAME", "BANK NAME"])

# =========================
# MONTH FILTER
# =========================
months = sorted(df["MONTH_NAME"].dropna().unique())

selected_month = st.selectbox("Month", months)

month_df = df[df["MONTH_NAME"] == selected_month]

# =========================
# BANK FILTER
# =========================
banks = sorted(month_df["BANK NAME"].dropna().unique())

selected_bank = st.selectbox("Bank", ["All Banks"] + banks)

if selected_bank != "All Banks":
    month_df = month_df[month_df["BANK NAME"] == selected_bank]

# =========================
# PIVOT TABLE
# =========================
pivot = pd.pivot_table(
    month_df,
    index="BANK NAME",
    columns="DAY",
    values="LC Number",
    aggfunc="count",
    fill_value=0
)

if not pivot.empty:
    pivot["Total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("Total", ascending=False)

st.subheader("Bank Wise Daily LC Count")
st.dataframe(pivot, use_container_width=True, height=600)

# =========================
# HEATMAP
# =========================
st.subheader("Branch Heatmap")

fig = branch_heatmap(month_df)
st.plotly_chart(fig, use_container_width=True)

# =========================
# LC NUMBERS (FULL MONTH VIEW - FIXED)
# =========================
st.subheader("LC Numbers (All Days of Selected Month)")

lc_columns = [
    "LC Number",
    "BANK NAME",
    "BRANCH",
    "RM",
    "Tracking Number",
    "DAY"
]

available_cols = [col for col in lc_columns if col in month_df.columns]

st.dataframe(
    month_df[available_cols],
    use_container_width=True,
    height=500
)

# =========================
# PDF REPORT
# =========================
if st.button("Generate PDF Report"):

    pdf_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    # safe bank name for file
    bank_name = selected_bank.replace(" ", "_")

    generate_pdf(
        pdf_file.name,
        selected_month,
        selected_bank,
        month_df
    )

    with open(pdf_file.name, "rb") as f:
        st.download_button(
            "Download PDF",
            f.read(),
            file_name=f"{bank_name}_{selected_month}.pdf",
            mime="application/pdf"
        )