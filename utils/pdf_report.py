from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd


def generate_pdf(
    filename,
    selected_month,
    selected_bank,
    df
):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()
    story = []

    # =========================
    # TITLE
    # =========================
    story.append(
        Paragraph(
            f"LC REPORT - {selected_bank} - {selected_month}",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 10))

    # =========================
    # SUMMARY
    # =========================
    story.append(Paragraph(f"<b>Total LC:</b> {len(df)}", styles["Normal"]))
    story.append(Spacer(1, 10))

    # =========================
    # BANK SUMMARY
    # =========================
    bank_summary = df.groupby("BANK NAME").size().reset_index(name="LC Count")

    table_data = [["Bank", "LC Count"]]

    for _, r in bank_summary.iterrows():
        table_data.append([r["BANK NAME"], r["LC Count"]])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)
    story.append(Spacer(1, 15))

    # =========================
    # 🔥 HEATMAP (BANK vs DAY)
    # =========================
    story.append(Paragraph("🔥 BANK vs DAY HEATMAP", styles["Heading2"]))
    story.append(Spacer(1, 8))

    heatmap = pd.pivot_table(
        df,
        index="BANK NAME",
        columns="DAY",
        values="LC Number",
        aggfunc="count",
        fill_value=0
    )

    heatmap["Total"] = heatmap.sum(axis=1)
    heatmap = heatmap.sort_values("Total", ascending=False)

    heat_data = [["Bank"] + list(heatmap.columns)]

    for idx, row in heatmap.iterrows():
        heat_data.append([idx] + list(row.values))

    heat_table = Table(heat_data)

    heat_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]

    # Heat coloring
    for i in range(1, len(heat_data)):
        for j in range(1, len(heat_data[0])):
            val = heat_data[i][j]

            if isinstance(val, (int, float)):
                if val == 0:
                    bg = colors.whitesmoke
                elif val < 3:
                    bg = colors.lightgreen
                elif val < 6:
                    bg = colors.yellow
                else:
                    bg = colors.red

                heat_style.append(("BACKGROUND", (j, i), (j, i), bg))

    heat_table.setStyle(TableStyle(heat_style))

    story.append(heat_table)
    story.append(Spacer(1, 15))

    # =========================
    # 📄 LC DETAILS TABLE (ALL DATA)
    # =========================
    story.append(Paragraph("📄 LC DETAILS", styles["Heading2"]))
    story.append(Spacer(1, 8))

    # REMOVE BANK NAME from table
    lc_df = df[["LC Number", "BRANCH", "RM", "DAY"]]

    lc_data = [lc_df.columns.tolist()]

    for _, row in lc_df.iterrows():
        lc_data.append(row.tolist())

    lc_table = Table(lc_data, repeatRows=1)

    lc_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))

    story.append(lc_table)

    doc.build(story)