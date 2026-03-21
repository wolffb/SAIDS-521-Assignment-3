"""
Mall Customer Segmentation Dashboard
=====================================
Interactive Plotly Dash dashboard with five visualizations and cross-filtering.

Run:
    conda activate siads521-dashboard
    python app.py

Then open http://127.0.0.1:8050 in your browser.
"""

import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Data loading and preparation
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Mall_Customers.csv")
df = pd.read_csv(DATA_PATH)
df.columns = ["CustomerID", "Gender", "Age", "Income", "SpendingScore"]

bins = [17, 25, 35, 45, 55, 70]
labels = ["18-25", "26-35", "36-45", "46-55", "56-70"]
df["AgeGroup"] = pd.cut(df["Age"], bins=bins, labels=labels)

COLOR_MAP = {"Male": "#636EFA", "Female": "#EF553B"}

# ---------------------------------------------------------------------------
# Dash app
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "Mall Customer Segmentation Dashboard"

app.layout = html.Div(
    style={"fontFamily": "Segoe UI, Arial, sans-serif", "margin": "0 auto",
           "maxWidth": "1400px", "padding": "20px"},
    children=[
        # Header
        html.H1("Mall Customer Segmentation Dashboard",
                style={"textAlign": "center", "marginBottom": "5px"}),
        html.P("Explore customer demographics, income, and spending behavior interactively.",
               style={"textAlign": "center", "color": "#666", "marginBottom": "25px"}),

        # Filters row
        html.Div(
            style={"display": "flex", "gap": "40px", "alignItems": "center",
                   "marginBottom": "25px", "flexWrap": "wrap",
                   "background": "#f8f9fa", "padding": "15px 20px",
                   "borderRadius": "8px"},
            children=[
                html.Div([
                    html.Label("Gender:", style={"fontWeight": "bold", "marginRight": "8px"}),
                    dcc.Dropdown(
                        id="gender-filter",
                        options=[
                            {"label": "All", "value": "All"},
                            {"label": "Male", "value": "Male"},
                            {"label": "Female", "value": "Female"},
                        ],
                        value="All",
                        clearable=False,
                        style={"width": "160px"},
                    ),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    html.Label("Age Range:", style={"fontWeight": "bold", "marginRight": "12px"}),
                    dcc.RangeSlider(
                        id="age-slider",
                        min=18, max=70, step=1,
                        value=[18, 70],
                        marks={i: str(i) for i in range(18, 71, 5)},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ], style={"flex": "1", "minWidth": "300px"}),
            ],
        ),

        # Row 1: Scatter + Bar
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(dcc.Graph(id="scatter-plot"), style={"flex": "1", "minWidth": "400px"}),
                html.Div(dcc.Graph(id="bar-chart"), style={"flex": "1", "minWidth": "400px"}),
            ],
        ),
        # Row 2: Histogram + Box
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"},
            children=[
                html.Div(dcc.Graph(id="histogram"), style={"flex": "1", "minWidth": "400px"}),
                html.Div(dcc.Graph(id="box-plot"), style={"flex": "1", "minWidth": "400px"}),
            ],
        ),
        # Row 3: Heatmap (centered)
        html.Div(
            style={"display": "flex", "justifyContent": "center"},
            children=[
                html.Div(dcc.Graph(id="heatmap"), style={"width": "500px"}),
            ],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Single callback — cross-filter all five charts
# ---------------------------------------------------------------------------
@app.callback(
    [
        Output("scatter-plot", "figure"),
        Output("bar-chart", "figure"),
        Output("histogram", "figure"),
        Output("box-plot", "figure"),
        Output("heatmap", "figure"),
    ],
    [
        Input("gender-filter", "value"),
        Input("age-slider", "value"),
    ],
)
def update_dashboard(gender, age_range):
    # Filter the dataframe
    filtered = df[(df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1])]
    if gender != "All":
        filtered = filtered[filtered["Gender"] == gender]

    # --- 1. Scatter Plot ---
    fig_scatter = px.scatter(
        filtered,
        x="Income",
        y="SpendingScore",
        color="Gender",
        hover_data=["Age", "CustomerID"],
        title="Annual Income vs. Spending Score",
        labels={"Income": "Annual Income (k$)", "SpendingScore": "Spending Score (1-100)"},
        color_discrete_map=COLOR_MAP,
        opacity=0.7,
    )
    fig_scatter.update_layout(template="plotly_white", height=400, margin=dict(t=40, b=30))

    # --- 2. Grouped Bar Chart ---
    agg = filtered.groupby("AgeGroup", observed=True)[["Income", "SpendingScore"]].mean().reset_index()
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=agg["AgeGroup"], y=agg["Income"],
        name="Avg Income (k$)", marker_color="#636EFA",
    ))
    fig_bar.add_trace(go.Bar(
        x=agg["AgeGroup"], y=agg["SpendingScore"],
        name="Avg Spending Score", marker_color="#EF553B",
    ))
    fig_bar.update_layout(
        barmode="group",
        title="Average Income & Spending Score by Age Group",
        xaxis_title="Age Group", yaxis_title="Value",
        template="plotly_white", height=400, margin=dict(t=40, b=30),
    )

    # --- 3. Histogram ---
    fig_hist = px.histogram(
        filtered,
        x="Age",
        color="Gender",
        nbins=15,
        barmode="stack",
        title="Age Distribution by Gender",
        labels={"Age": "Age (years)", "count": "Number of Customers"},
        color_discrete_map=COLOR_MAP,
    )
    fig_hist.update_layout(template="plotly_white", height=400, margin=dict(t=40, b=30))

    # --- 4. Box Plots ---
    fig_box = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Annual Income by Gender", "Spending Score by Gender"),
    )
    for i, col in enumerate(["Income", "SpendingScore"], 1):
        for g, color in [("Male", "#636EFA"), ("Female", "#EF553B")]:
            subset = filtered[filtered["Gender"] == g]
            fig_box.add_trace(
                go.Box(y=subset[col], name=g, marker_color=color,
                       showlegend=(i == 1)),
                row=1, col=i,
            )
    fig_box.update_layout(
        title="Income & Spending Score Distributions by Gender",
        template="plotly_white", height=400, margin=dict(t=50, b=30),
    )

    # --- 5. Heatmap ---
    corr_cols = ["Age", "Income", "SpendingScore"]
    if len(filtered) >= 2:
        corr_matrix = filtered[corr_cols].corr()
    else:
        corr_matrix = pd.DataFrame(np.zeros((3, 3)), index=corr_cols, columns=corr_cols)
    fig_heat = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_cols,
        y=corr_cols,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
    ))
    fig_heat.update_layout(
        title="Correlation Matrix",
        template="plotly_white", height=400, width=480,
        margin=dict(t=40, b=30),
    )

    return fig_scatter, fig_bar, fig_hist, fig_box, fig_heat


# ---------------------------------------------------------------------------
# Run the server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
