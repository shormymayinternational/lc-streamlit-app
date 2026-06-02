import plotly.express as px

def branch_heatmap(df):

    branch_summary = (
        df.groupby("BRANCH")
        .size()
        .reset_index(name="LC Count")
    )

    fig = px.density_heatmap(
        branch_summary,
        x="BRANCH",
        y=["LC"] * len(branch_summary),
        z="LC Count"
    )

    return fig