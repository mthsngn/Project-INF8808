"""
INF8808
Exécution :
    pip install dash pandas numpy plotly
    python viz2.py
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# -----------------------------
# Données
# -----------------------------
# def make_fake_olympics_data(n=2500, seed=7) -> pd.DataFrame:
#     rng = np.random.default_rng(seed)

#     sports = ["Biathlon", "Speed Skating", "Ice Hockey"]
#     sport = rng.choice(sports, size=n, p=[0.33, 0.33, 0.34])

#     sex = rng.choice(["F", "M"], size=n, p=[0.45, 0.55])

#     years = rng.choice(
#         [1998, 2002, 2006, 2010, 2014, 2018, 2022],
#         size=n,
#         p=[0.12, 0.12, 0.12, 0.14, 0.16, 0.17, 0.17],
#     )

#     height = np.empty(n)
#     weight = np.empty(n)
#     age = np.empty(n)

#     for i, s in enumerate(sport):
#         if s == "Biathlon":
#             if sex[i] == "M":
#                 height[i] = rng.normal(181, 6)
#                 weight[i] = rng.normal(76, 7)
#                 age[i] = rng.normal(27.5, 3.8)
#             else:
#                 height[i] = rng.normal(168, 6)
#                 weight[i] = rng.normal(61, 6)
#                 age[i] = rng.normal(26.5, 3.8)

#         elif s == "Speed Skating":
#             if sex[i] == "M":
#                 height[i] = rng.normal(179, 7)
#                 weight[i] = rng.normal(75, 8)
#                 age[i] = rng.normal(26.5, 4.0)
#             else:
#                 height[i] = rng.normal(167, 6)
#                 weight[i] = rng.normal(62, 7)
#                 age[i] = rng.normal(25.8, 4.0)

#         else:  # Ice Hockey
#             if sex[i] == "M":
#                 height[i] = rng.normal(185, 6)
#                 weight[i] = rng.normal(88, 9)
#                 age[i] = rng.normal(25.8, 3.8)
#             else:
#                 height[i] = rng.normal(171, 6)
#                 weight[i] = rng.normal(69, 7)
#                 age[i] = rng.normal(24.8, 3.8)

#     t = years - 1998
#     height = height + 0.03 * t + rng.normal(0, 0.6, size=n)
#     weight = weight + 0.05 * t + rng.normal(0, 0.7, size=n)
#     age = age + 0.01 * t + rng.normal(0, 0.4, size=n)

#     height = np.clip(height, 145, 210)
#     weight = np.clip(weight, 45, 140)
#     age = np.clip(age, 15, 45)

#     medal = []
#     for i in range(n):
#         score = 0.0

#         if sport[i] == "Biathlon":
#             score += 0.10 * (age[i] - 24) - 0.02 * abs(weight[i] - 72)
#         elif sport[i] == "Speed Skating":
#             score += 0.08 * (height[i] - 172) - 0.02 * abs(age[i] - 26)
#         else:
#             score += 0.06 * (weight[i] - 80) - 0.02 * abs(height[i] - 184)

#         score += rng.normal(0, 0.2)

#         p_gold = np.clip(0.04 + 0.01 * score, 0.01, 0.08)
#         p_silver = np.clip(0.06 + 0.01 * score, 0.02, 0.10)
#         p_bronze = np.clip(0.08 + 0.01 * score, 0.03, 0.12)
#         p_none = max(0.0, 1.0 - (p_gold + p_silver + p_bronze))

#         medal.append(
#             rng.choice(
#                 ["Gold", "Silver", "Bronze", "None"],
#                 p=[p_gold, p_silver, p_bronze, p_none],
#             )
#         )

#     iso3 = ["CAN", "USA", "FRA", "NOR", "SWE", "FIN", "GER", "ITA", "JPN", "CHN", "KOR", "SUI", "GBR", "AUT"]
#     country_noc = rng.choice(iso3, size=n)
#     athlete = [f"Athlete_{i:04d}" for i in range(1, n + 1)]

#     return pd.DataFrame(
#         {
#             "athlete": athlete,
#             "sport": sport,
#             "sex": sex,
#             "year": years,
#             "age": np.round(age, 1),
#             "height_cm": np.round(height, 1),
#             "weight_kg": np.round(weight, 1),
#             "medal": medal,
#             "country_noc": country_noc,
#         }
#     )

def load_and_preprocess_data(event_results_path: str) -> pd.DataFrame:
    df = pd.read_csv(event_results_path)

    selected_sports = ["Biathlon", "Ice Hockey", "Speed Skating"]
    df = df[df["sport"].isin(selected_sports)].copy()

    df = df[
        [
            "sport",
            "medal",
            "country_noc",
            "athlete",
            "athlete_id",
        ]
    ].copy()

    # On garde seulement les lignes ayant un pays et un sport
    df = df.dropna(subset=["sport", "country_noc"])

    # Uniformiser les médailles
    df["medal"] = df["medal"].fillna("None")

    # Nettoyage léger des codes pays
    df["country_noc"] = df["country_noc"].astype(str).str.strip()

    return df


# -----------------------------
# Config
# -----------------------------
COUNTRY_NAMES = { # code -> libellé complet TO DO
    "CAN": "Canada",
    "USA": "United States",
    "FRA": "France",
    "NOR": "Norway",
    "SWE": "Sweden",
    "FIN": "Finland",
    "GER": "Germany",
    "ITA": "Italy",
    "JPN": "Japan",
    "CHN": "China",
    "KOR": "South Korea",
    "SUI": "Switzerland",
    "GBR": "United Kingdom",
    "AUT": "Austria",
}

SPORT_OPTIONS = [
    {"label": "Tous", "value": "All"},
    {"label": "Biathlon", "value": "Biathlon"},
    {"label": "Ice Hockey", "value": "Ice Hockey"},
    {"label": "Speed Skating", "value": "Speed Skating"},
]

MEDAL_ORDER = ["Gold", "Silver", "Bronze"]
MEDAL_COLORS = {
    "Gold": "#D4AF37",
    "Silver": "#C0C0C0",
    "Bronze": "#CD7F32",
}


# -----------------------------
# Filtrage
# -----------------------------
def apply_sport_filter_for_medals(df: pd.DataFrame, selected_sport: str) -> pd.DataFrame:
    dff = df[df["medal"].isin(["Gold", "Silver", "Bronze"])].copy()

    if selected_sport != "All":
        dff = dff[dff["sport"] == selected_sport]

    return dff


# -----------------------------
# Figures
# -----------------------------
def make_choropleth_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:
    dff = apply_sport_filter_for_medals(df, selected_sport)

    agg = (
        dff.groupby("country_noc", as_index=False)
        .size()
        .rename(columns={"size": "medals"})
    )

    agg["country_name"] = agg["country_noc"].map(COUNTRY_NAMES)

    pink_scale = [
        [0.0, "#fde0ef"],
        [0.2, "#f9b3d4"],
        [0.4, "#f57ab4"],
        [0.6, "#e74a9e"],
        [0.8, "#c51b8a"],
        [1.0, "#7a0177"],
    ]

    max_z = max(1, int(agg["medals"].max())) if not agg.empty else 1

    fig = go.Figure()

    fig.add_trace(
        go.Choropleth(
            locations=agg["country_noc"] if not agg.empty else [],
            z=agg["medals"] if not agg.empty else [],
            locationmode="ISO-3",
            text=agg["country_name"] if not agg.empty else [],
            colorscale=pink_scale,
            zmin=0,
            zmax=max_z,
            marker_line_color="white",
            marker_line_width=0.8,
            colorbar_title="Médailles",
            hovertemplate="<b>%{text}</b><br>Médailles: %{z}<extra></extra>",
        )
    )

    title = "Carte géographique des médailles"
    if selected_sport != "All":
        title += f" - {selected_sport}"

    fig.update_layout(
        title=title,
        margin=dict(l=20, r=20, t=70, b=20),
        template="plotly_white",
        geo=dict(
            projection_type="natural earth",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="white",
            showcountries=True,
            countrycolor="white",
            showland=True,
            landcolor="#eaf1f8",
            showocean=True,
            oceancolor="#c7dff2",
            showlakes=True,
            lakecolor="#c7dff2",
            bgcolor="#c7dff2",
        ),
    )

    return fig


def make_barchart_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:
    dff = apply_sport_filter_for_medals(df, selected_sport)

    if dff.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Distribution des médailles par pays",
            xaxis_title="Pays",
            yaxis_title="Nombre de médailles",
            template="plotly_white",
            margin=dict(l=50, r=30, t=70, b=80),
        )
        return fig

    agg = (
        dff.groupby(["country_noc", "medal"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    all_countries = sorted(dff["country_noc"].unique().tolist())
    full_index = pd.MultiIndex.from_product(
        [all_countries, MEDAL_ORDER],
        names=["country_noc", "medal"]
    )

    agg = (
        agg.set_index(["country_noc", "medal"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )

    agg["country_name"] = agg["country_noc"].map(COUNTRY_NAMES)

    totals = (
        agg.groupby("country_noc", as_index=False)["count"]
        .sum()
        .rename(columns={"count": "total_medals"})
    )

    agg = agg.merge(totals, on="country_noc", how="left")

    country_order = (
        totals.sort_values("total_medals", ascending=False)["country_noc"].tolist()
    )

    agg["country_noc"] = pd.Categorical(
        agg["country_noc"],
        categories=country_order,
        ordered=True,
    )

    agg = agg.sort_values(["country_noc", "medal"])

    fig = go.Figure()

    for medal in MEDAL_ORDER:
        dm = agg[agg["medal"] == medal]

        fig.add_trace(
            go.Bar(
                x=dm["country_name"],
                y=dm["count"],
                name=medal,
                marker_color=MEDAL_COLORS[medal],
                customdata=np.stack(
                    [dm["country_noc"].astype(str), dm["total_medals"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"Type: {medal}<br>"
                    "Nombre de médailles: %{y}<br>"
                    "Total du pays: %{customdata[1]}"
                    "<extra></extra>"
                ),
            )
        )

    title = "Distribution des médailles par pays"
    if selected_sport != "All":
        title += f" - {selected_sport}"

    fig.update_layout(
        title=title,
        xaxis_title="Pays",
        yaxis_title="Nombre de médailles",
        barmode="group",
        legend_title_text="Type de médaille",
        margin=dict(l=50, r=30, t=70, b=90),
        bargap=0.18,
        bargroupgap=0.08,
        template="plotly_white",
    )

    fig.update_xaxes(
        tickangle=-45,
        tickfont=dict(size=11),
        automargin=True,
    )

    fig.update_yaxes(
        tickfont=dict(size=11),
        rangemode="tozero",
    )

    return fig


# -----------------------------
# App Dash
# -----------------------------
df = load_and_preprocess_data(
    event_results_path="data/Olympic_Athlete_Event_Results.csv"
)
app = Dash(__name__)

card_style = {
    "backgroundColor": "white",
    "border": "1px solid #e6e6e6",
    "borderRadius": "12px",
    "padding": "16px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
}

section_title_style = {
    "margin": "0 0 12px 0",
    "fontSize": "20px",
    "fontWeight": "700",
}

section_subtitle_style = {
    "margin": "0 0 14px 0",
    "fontSize": "13px",
    "color": "#666",
}

app.layout = html.Div(
    style={
        "padding": "24px",
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f7f8fa",
        "maxWidth": "1100px",
        "margin": "0 auto",
    },
    children=[
        html.H2("Répartition géographique des médailles", style={"marginBottom": "18px"}),

        html.Div(
            style=card_style,
            children=[
                html.H3("Pays et types de médailles", style=section_title_style),
                html.Div(
                    style={"marginBottom": "18px"},
                    children=[
                        html.Label(
                            "Sport",
                            style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"},
                        ),
                        dcc.RadioItems(
                            id="sport-filter",
                            options=SPORT_OPTIONS,
                            value="All",
                            inline=True,
                            inputStyle={"marginRight": "6px", "marginLeft": "12px"},
                        ),
                    ],
                ),

                # Bar chart en premier
                html.Div(
                    style={"marginBottom": "24px"},
                    children=[
                        dcc.Graph(
                            id="fig4-barchart",
                            config={"displayModeBar": False},
                            style={"height": "520px"},
                        )
                    ],
                ),

                # Carte en dessous
                html.Div(
                    children=[
                        dcc.Graph(
                            id="fig4-map",
                            config={"displayModeBar": False},
                            style={"height": "520px"},
                        )
                    ],
                ),
            ],
        ),
    ],
)


# -----------------------------
# Callback
# -----------------------------
@app.callback(
    Output("fig4-map", "figure"),
    Output("fig4-barchart", "figure"),
    Input("sport-filter", "value"),
)
def update_figures(selected_sport):
    fig_map = make_choropleth_figure(df, selected_sport=selected_sport)
    fig_bar = make_barchart_figure(df, selected_sport=selected_sport)
    return fig_map, fig_bar


if __name__ == "__main__":
    app.run(debug=True)