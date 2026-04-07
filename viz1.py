"""
INF8808
Exécution :
    pip install dash pandas numpy plotly
    python viz1.py
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


# -----------------------------
# Données
# -----------------------------
def load_and_preprocess_data(event_results_path: str, athlete_bio_path: str, games_path: str) -> pd.DataFrame:
    df_results = pd.read_csv(event_results_path)
    df_bio = pd.read_csv(athlete_bio_path)
    df_games = pd.read_csv(games_path)

    # -----------------------------
    # Filtrer les sports d'hiver d'intérêt
    # -----------------------------
    selected_sports = ["Biathlon", "Ice Hockey", "Speed Skating"]
    df_results = df_results[df_results["sport"].isin(selected_sports)].copy()

    # -----------------------------
    # Sélectionner seulement les colonnes utiles
    # -----------------------------
    df_results = df_results[
        [
            "edition_id",
            "country_noc",
            "sport",
            "athlete_id",
            "athlete",
            "medal",
        ]
    ].copy()

    df_bio = df_bio[
        [
            "athlete_id",
            "name",
            "sex",
            "born",
            "height",
            "weight",
            "country_noc",
        ]
    ].copy()

    df_games = df_games[
        [
            "edition_id",
            "year",
            "edition",
        ]
    ].copy()

    # -----------------------------
    # Jointures
    # -----------------------------
    df = df_results.merge(df_bio, on="athlete_id", how="left", suffixes=("", "_bio"))
    df = df.merge(df_games, on="edition_id", how="left")

    # -----------------------------
    # Nettoyage des variables
    # -----------------------------

    # sexe : Male/Female -> M/F
    df["sex"] = df["sex"].replace(
        {
            "Male": "M",
            "Female": "F",
        }
    )

    # médaille : les non-médaillés ont NaN
    df["medal"] = df["medal"].fillna("None")

    # year en numérique
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # born : extraire l'année de naissance
    df["born_year"] = (
        df["born"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
    )
    df["born_year"] = pd.to_numeric(df["born_year"], errors="coerce")

    # height / weight en numérique
    df["height_cm"] = pd.to_numeric(df["height"], errors="coerce")
    df["weight_kg"] = pd.to_numeric(df["weight"], errors="coerce")

    # âge
    df["age"] = df["year"] - df["born_year"]

    # nom d'athlète
    # athlete : garder celui des résultats en priorité
    df["athlete"] = df["athlete"].fillna(df["name"])

    # country_noc : garder celui des résultats en priorité
    if "country_noc_bio" in df.columns:
        df["country_noc"] = df["country_noc"].fillna(df["country_noc_bio"])

    # -----------------------------
    # Filtrer les lignes inutilisables
    # -----------------------------
    df = df.dropna(subset=["sport", "sex", "year"])

    # garde seulement les lignes ayant au moins une variable physiologique utile
    df = df[
        df["age"].notna() |
        df["height_cm"].notna() |
        df["weight_kg"].notna()
    ].copy()

    # -----------------------------
    # Colonnes finales
    # -----------------------------
    df = df[
        [
            "athlete",
            "sport",
            "sex",
            "year",
            "age",
            "height_cm",
            "weight_kg",
            "medal",
            "country_noc",
        ]
    ].copy()

    return df


# -----------------------------
# Config
# -----------------------------
VARIABLES = {
    "age": {"label": "Âge (années)", "column": "age"},
    "height_cm": {"label": "Taille (cm)", "column": "height_cm"},
    "weight_kg": {"label": "Poids (kg)", "column": "weight_kg"},
}

SPORT_OPTIONS = [
    {"label": "Tous", "value": "All"},
    {"label": "Biathlon", "value": "Biathlon"},
    {"label": "Ice Hockey", "value": "Ice Hockey"},
    {"label": "Speed Skating", "value": "Speed Skating"},
]

SEX_OPTIONS = [
    {"label": "Tous", "value": "All"},
    {"label": "M", "value": "M"},
    {"label": "F", "value": "F"},
]

MEDAL_FILTER_OPTIONS = [
    {"label": "Tous", "value": "All"},
    {"label": "Uniquement médaillés", "value": "Medaled"},
]


# -----------------------------
# Filtres
# -----------------------------
def apply_global_filters(df: pd.DataFrame, selected_sex: str, selected_medal_filter: str) -> pd.DataFrame:
    dff = df.copy()

    if selected_sex != "All":
        dff = dff[dff["sex"] == selected_sex]

    if selected_medal_filter == "Medaled":
        dff = dff[dff["medal"] != "None"]

    return dff


def apply_scatter_sport_filter(df: pd.DataFrame, selected_sport: str) -> pd.DataFrame:
    if selected_sport == "All":
        return df
    return df[df["sport"] == selected_sport]


# -----------------------------
# Figures
# -----------------------------
def make_boxplot_figure(df: pd.DataFrame, variable_key: str) -> go.Figure:
    info = VARIABLES[variable_key]
    col = info["column"]
    label = info["label"]

    sports_order = ["Biathlon", "Ice Hockey", "Speed Skating"]
    colors = {
        "Biathlon": "#222222",
        "Ice Hockey": "#222222",
        "Speed Skating": "#222222",
    }

    fig = go.Figure()

    for sport_name in sports_order:
        d = df[df["sport"] == sport_name]
        if d.empty:
            continue

        fig.add_trace(
            go.Box(
                x=[sport_name] * len(d),
                y=d[col],
                name=sport_name,
                boxpoints="outliers",
                marker=dict(color=colors[sport_name]),
                line=dict(color=colors[sport_name]),
                fillcolor="rgba(255,255,255,0.88)",
                hovertemplate=(
                    f"Discipline: {sport_name}<br>"
                    f"{label}: %{{y}}<br>"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

    fig.update_layout(
        title=f"Distribution - {label} par discipline",
        xaxis_title="Discipline",
        yaxis_title=label,
        margin=dict(l=50, r=30, t=70, b=50),
        template="plotly_white",
    )
    return fig


def make_scatter_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:
    dff = apply_scatter_sport_filter(df, selected_sport)

    medal_order = ["Gold", "Silver", "Bronze", "None"]
    medal_styles = {
        "Gold": dict(color="#D4AF37", line=dict(color="#8c6d1f", width=1)),
        "Silver": dict(color="#C0C0C0", line=dict(color="#7a7a7a", width=1)),
        "Bronze": dict(color="#CD7F32", line=dict(color="#8a5522", width=1)),
        "None": dict(color="white", line=dict(color="#666", width=1.2)),
    }

    fig = go.Figure()

    for medal in medal_order:
        dm = dff[dff["medal"] == medal]
        if dm.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=dm["height_cm"],
                y=dm["weight_kg"],
                mode="markers",
                name=medal,
                marker=dict(size=8, opacity=0.68, **medal_styles[medal]),
                customdata=np.stack(
                    [dm["athlete"], dm["sport"], dm["sex"], dm["year"], dm["age"]],
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Discipline: %{customdata[1]}<br>"
                    "Sexe: %{customdata[2]}<br>"
                    "Année: %{customdata[3]}<br>"
                    "Âge: %{customdata[4]}<br>"
                    "Taille: %{x} cm<br>"
                    "Poids: %{y} kg<br>"
                    f"Médaille: {medal}"
                    "<extra></extra>"
                ),
            )
        )

    title = "Relation taille / poids"
    if selected_sport != "All":
        title += f" - {selected_sport}"

    fig.update_layout(
        title=title,
        xaxis_title="Taille (cm)",
        yaxis_title="Poids (kg)",
        legend_title_text="Médaille",
        margin=dict(l=50, r=30, t=70, b=50),
        template="plotly_white",
    )
    return fig


def make_trend_figure(df: pd.DataFrame, variable_key: str) -> go.Figure:
    info = VARIABLES[variable_key]
    col = info["column"]
    label = info["label"]

    agg = (
        df.dropna(subset=["year", "sport", col])
        .groupby(["year", "sport"], as_index=False)[col]
        .mean()
        .rename(columns={col: "value"})
    )

    sports_order = ["Biathlon", "Ice Hockey", "Speed Skating"]
    neutral_colors = {
        "Biathlon": "#222222",
        "Ice Hockey": "#222222",
        "Speed Skating": "#222222",
    }

    fig = go.Figure()

    for sport_name in sports_order:
        d = agg[agg["sport"] == sport_name].sort_values("year").copy()
        if d.empty:
            continue

        text_labels = [""] * len(d)
        text_labels[-1] = sport_name

        fig.add_trace(
            go.Scatter(
                x=d["year"],
                y=d["value"],
                mode="lines+markers+text",
                name=sport_name,
                line=dict(color=neutral_colors[sport_name], width=2),
                marker=dict(size=6, color=neutral_colors[sport_name]),
                text=text_labels,
                textposition="middle right",
                textfont=dict(size=12, color=neutral_colors[sport_name]),
                hovertemplate=(
                    f"Discipline: {sport_name}<br>"
                    "Année: %{x}<br>"
                    f"{label}: %{{y:.2f}}<extra></extra>"
                ),
                cliponaxis=False,
                showlegend=False,
            )
        )

    fig.update_layout(
        title=f"Évolution temporelle - {label}",
        xaxis_title="Année (Jeux Olympiques d’hiver)",
        yaxis_title=label,
        margin=dict(l=50, r=90, t=70, b=50),
        template="plotly_white",
        showlegend=False,
    )
    return fig


# -----------------------------
# App Dash
# -----------------------------
df = load_and_preprocess_data(
    event_results_path="data/Olympic_Athlete_Event_Results.csv",
    athlete_bio_path="data/Olympic_Athlete_Bio.csv",
    games_path="data/Olympics_Games.csv",
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
        "maxWidth": "1400px",
        "margin": "0 auto",
    },
    children=[
        html.H2("Profils physiologiques", style={"marginBottom": "18px"}),

        # Filtres globaux
        html.Div(
            style={**card_style, "marginBottom": "22px"},
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "28px",
                        "alignItems": "flex-start",
                        "flexWrap": "wrap",
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Label("Sexe", style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"}),
                                dcc.RadioItems(
                                    id="sex-filter",
                                    options=SEX_OPTIONS,
                                    value="All",
                                    inline=True,
                                    inputStyle={"marginRight": "6px", "marginLeft": "12px"},
                                ),
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Label("Médailles", style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"}),
                                dcc.RadioItems(
                                    id="medal-filter",
                                    options=MEDAL_FILTER_OPTIONS,
                                    value="All",
                                    inline=True,
                                    inputStyle={"marginRight": "6px", "marginLeft": "12px"},
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),

        # Conteneur côte à côte pour les 2 blocs
        html.Div(
            style={
                "display": "flex",
                "gap": "22px",
                "alignItems": "stretch",
                "flexWrap": "wrap",  # repasse en colonne si écran trop petit
            },
            children=[
                # Bloc 1 — plus large
                html.Div(
                    style={**card_style, "flex": "1.5", "minWidth": "700px"},
                    children=[
                        html.H3("Profils physiologiques", style=section_title_style),
                        html.Div(
                            style={"marginBottom": "16px"},
                            children=[
                                html.Label(
                                    "Variable",
                                    style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"},
                                ),
                                dcc.RadioItems(
                                    id="variable-radio",
                                    options=[
                                        {"label": "Âge", "value": "age"},
                                        {"label": "Taille", "value": "height_cm"},
                                        {"label": "Poids", "value": "weight_kg"},
                                    ],
                                    value="age",
                                    inline=True,
                                    inputStyle={"marginRight": "6px", "marginLeft": "12px"},
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                dcc.Graph(id="fig1-boxplot", config={"displayModeBar": False}),
                                dcc.Graph(id="fig3-trend", config={"displayModeBar": False}),
                            ]
                        ),
                    ],
                ),

                # Bloc 2 — plus étroit
                html.Div(
                    style={**card_style, "flex": "1", "minWidth": "420px", "alignSelf": "flex-start"},
                    children=[
                        html.H3("Relation taille / poids", style=section_title_style),
                        html.Div(
                            style={"marginBottom": "14px"},
                            children=[
                                html.Label(
                                    "Sport",
                                    style={"fontWeight": "bold", "display": "block", "marginBottom": "8px"},
                                ),
                                dcc.RadioItems(
                                    id="scatter-sport-filter",
                                    options=SPORT_OPTIONS,
                                    value="All",
                                    inline=True,
                                    inputStyle={"marginRight": "6px", "marginLeft": "12px"},
                                ),
                            ],
                        ),
                        dcc.Graph(id="fig2-scatter", config={"displayModeBar": False}),
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
    Output("fig1-boxplot", "figure"),
    Output("fig2-scatter", "figure"),
    Output("fig3-trend", "figure"),
    Input("sex-filter", "value"),
    Input("medal-filter", "value"),
    Input("variable-radio", "value"),
    Input("scatter-sport-filter", "value"),
)
def update_figures(selected_sex, selected_medal_filter, variable_key, selected_scatter_sport):
    dff_global = apply_global_filters(
        df=df,
        selected_sex=selected_sex,
        selected_medal_filter=selected_medal_filter,
    )

    fig1 = make_boxplot_figure(dff_global, variable_key=variable_key)
    fig2 = make_scatter_figure(dff_global, selected_sport=selected_scatter_sport)
    fig3 = make_trend_figure(dff_global, variable_key=variable_key)

    return fig1, fig2, fig3


if __name__ == "__main__":
    app.run(debug=True)
