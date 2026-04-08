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



# Configuration

SELECTED_SPORTS      = ["Biathlon", "Hockey sur glace", "Patinage de vitesse"]
ENGLISH_SPORTS_FILTER = ["Biathlon", "Ice Hockey", "Speed Skating"]

SPORT_COLORS = {
    "Biathlon": "#5B6CFF",
    "Hockey sur glace": "#FF7A59",
    "Patinage de vitesse": "#22A699",
}

VARIABLES = {
    "age": {"label": "Âge (années)", "column": "age"},
    "height_cm": {"label": "Taille (cm)", "column": "height_cm"},
    "weight_kg": {"label": "Poids (kg)", "column": "weight_kg"},
}

SEX_OPTIONS = [
    {"label": "Tous", "value": "All"},
    {"label": "M", "value": "M"},
    {"label": "F", "value": "F"},
]

MEDAL_FILTER_OPTIONS = [
    {"label": "Tous", "value": "All"},
    {"label": "Uniquement médaillés", "value": "Medaled"},
]

VARIABLE_OPTIONS = [
    {"label": "Âge", "value": "age"},
    {"label": "Taille", "value": "height_cm"},
    {"label": "Poids", "value": "weight_kg"},
]

SPORT_OPTIONS = [
    {"label": "Tous", "value": "All"},
    {"label": "Biathlon", "value": "Biathlon"},
    {"label": "Hockey sur glace", "value": "Hockey sur glace"},
    {"label": "Patinage de vitesse", "value": "Patinage de vitesse"},
]



# Helpers

def _id(prefix: str, name: str) -> str:
    return f"{prefix}-{name}"


def _validate_columns(df: pd.DataFrame, required_columns: list[str], df_name: str) -> None:
    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {df_name}: {sorted(missing)}")


def make_empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text=message,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=15, color="#6B7280"),
            )
        ],
    )
    return fig


def apply_common_layout(fig: go.Figure, title: str, x_title: str = "", y_title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left"),
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color="#1F2937"),
        margin=dict(l=55, r=25, t=60, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    fig.update_xaxes(
        showline=True,
        linecolor="#D1D5DB",
        gridcolor="#E5E7EB",
        zeroline=False,
    )
    fig.update_yaxes(
        showline=True,
        linecolor="#D1D5DB",
        gridcolor="#E5E7EB",
        zeroline=False,
    )
    return fig



# Chargement et prétraitement des données

def load_and_preprocess_data(
    event_results_path: str,
    athlete_bio_path: str,
    games_path: str,
) -> pd.DataFrame:
    df_results = pd.read_csv(event_results_path)
    df_bio = pd.read_csv(athlete_bio_path)
    df_games = pd.read_csv(games_path)

    _validate_columns(
        df_results,
        ["edition_id", "country_noc", "sport", "athlete_id", "athlete", "medal"],
        "df_results",
    )
    _validate_columns(
        df_bio,
        ["athlete_id", "name", "sex", "born", "height", "weight", "country_noc"],
        "df_bio",
    )
    _validate_columns(
        df_games,
        ["edition_id", "year", "edition"],
        "df_games",
    )

    df_results = df_results[df_results["sport"].isin(ENGLISH_SPORTS_FILTER)].copy()

    df_results = df_results[
        ["edition_id", "country_noc", "sport", "athlete_id", "athlete", "medal"]
    ].copy()

    df_bio = df_bio[
        ["athlete_id", "name", "sex", "born", "height", "weight", "country_noc"]
    ].copy()

    df_games = df_games[["edition_id", "year", "edition"]].copy()

    df = df_results.merge(df_bio, on="athlete_id", how="left", suffixes=("", "_bio"))
    df = df.merge(df_games, on="edition_id", how="left")

    df["sex"] = df["sex"].replace({"Male": "M", "Female": "F"})
    df["medal"] = df["medal"].fillna("Aucune")

    # Traduction des valeurs en français
    df["medal"] = df["medal"].replace({
        "Gold": "Or", "Silver": "Argent", "Bronze": "Bronze", "None": "Aucune"
    })
    df["sport"] = df["sport"].replace({
        "Ice Hockey": "Hockey sur glace", "Speed Skating": "Patinage de vitesse"
    })
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    df["born_year"] = df["born"].astype(str).str.extract(r"(\d{4})")[0]
    df["born_year"] = pd.to_numeric(df["born_year"], errors="coerce")

    df["height_cm"] = pd.to_numeric(df["height"], errors="coerce")
    df["weight_kg"] = pd.to_numeric(df["weight"], errors="coerce")
    df["age"] = df["year"] - df["born_year"]

    df["athlete"] = df["athlete"].fillna(df["name"]).fillna("Athlète inconnu")

    if "country_noc_bio" in df.columns:
        df["country_noc"] = df["country_noc"].fillna(df["country_noc_bio"])

    df = df.dropna(subset=["sport", "sex", "year"]).copy()

    df.loc[~df["age"].between(12, 60), "age"] = np.nan
    df.loc[~df["height_cm"].between(120, 230), "height_cm"] = np.nan
    df.loc[~df["weight_kg"].between(35, 180), "weight_kg"] = np.nan

    df = df[
        df["age"].notna()
        | df["height_cm"].notna()
        | df["weight_kg"].notna()
    ].copy()

    df = df.drop_duplicates(subset=["athlete_id", "sport", "year"]).copy()

    df = df[
        [
            "athlete_id",
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



# Filtres

def apply_global_filters(
    df: pd.DataFrame,
    selected_sex: str,
    selected_medal_filter: str,
) -> pd.DataFrame:
    dff = df.copy()

    if selected_sex != "All":
        dff = dff[dff["sex"] == selected_sex]

    if selected_medal_filter == "Medaled":
        dff = dff[dff["medal"] != "Aucune"]

    return dff


def apply_scatter_sport_filter(df: pd.DataFrame, selected_sport: str) -> pd.DataFrame:
    if selected_sport == "All":
        return df
    return df[df["sport"] == selected_sport].copy()



# Figures

def make_boxplot_figure(df: pd.DataFrame, variable_key: str) -> go.Figure:
    info = VARIABLES[variable_key]
    col = info["column"]
    label = info["label"]

    dff = df.dropna(subset=[col]).copy()
    if dff.empty:
        return make_empty_figure("Aucune donnée disponible pour ce boxplot.")

    fig = go.Figure()

    for sport_name in SELECTED_SPORTS:
        d = dff[dff["sport"] == sport_name]
        if d.empty:
            continue

        fig.add_trace(
            go.Box(
                y=d[col],
                name=sport_name,
                boxpoints="outliers",
                marker=dict(color=SPORT_COLORS[sport_name]),
                line=dict(color=SPORT_COLORS[sport_name]),
                fillcolor="rgba(255,255,255,0.65)",
                hovertemplate=(
                    f"Sport: {sport_name}<br>"
                    f"{label}: %{{y:.2f}}<extra></extra>"
                ),
            )
        )

    fig = apply_common_layout(
        fig,
        title=f"Distribution de {label.lower()} par discipline",
        x_title="Discipline",
        y_title=label,
    )
    fig.update_layout(showlegend=False)
    return fig


def make_scatter_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:
    dff = apply_scatter_sport_filter(df, selected_sport)
    dff = dff.dropna(subset=["height_cm", "weight_kg"]).copy()

    if dff.empty:
        return make_empty_figure("Aucune donnée disponible pour ce nuage de points.")

    medal_order = ["Or", "Argent", "Bronze", "Aucune"]
    medal_styles = {
        "Or": dict(color="#D4AF37", line=dict(color="#8B6A16", width=1)),
        "Argent": dict(color="#C0C0C0", line=dict(color="#7C7C7C", width=1)),
        "Bronze": dict(color="#CD7F32", line=dict(color="#8A5522", width=1)),
        "Aucune": dict(color="#FFFFFF", line=dict(color="#6B7280", width=1.2)),
    }

    fig = go.Figure()

    for medal in medal_order:
        dm = dff[dff["medal"] == medal]
        if dm.empty:
            continue

        customdata = np.column_stack(
            [
                dm["athlete"].fillna("Athlète inconnu"),
                dm["sport"].fillna("NA"),
                dm["sex"].fillna("NA"),
                dm["year"].fillna("NA"),
                dm["age"].round(1).fillna("NA"),
            ]
        )

        fig.add_trace(
            go.Scatter(
                x=dm["height_cm"],
                y=dm["weight_kg"],
                mode="markers",
                name=medal,
                marker=dict(size=9, opacity=0.72, **medal_styles[medal]),
                customdata=customdata,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Sport: %{customdata[1]}<br>"
                    "Sexe: %{customdata[2]}<br>"
                    "Année: %{customdata[3]}<br>"
                    "Âge: %{customdata[4]}<br>"
                    "Taille: %{x:.1f} cm<br>"
                    "Poids: %{y:.1f} kg<br>"
                    f"Médaille: {medal}<extra></extra>"
                ),
            )
        )

    title = "Relation taille / poids"
    if selected_sport != "All":
        title += f" — {selected_sport}"

    fig = apply_common_layout(
        fig,
        title=title,
        x_title="Taille (cm)",
        y_title="Poids (kg)",
    )
    fig.update_layout(legend_title_text="Médaille")
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

    if agg.empty:
        return make_empty_figure("Aucune donnée disponible pour la tendance temporelle.")

    fig = go.Figure()

    for sport_name in SELECTED_SPORTS:
        d = agg[agg["sport"] == sport_name].sort_values("year").copy()
        if d.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=d["year"],
                y=d["value"],
                mode="lines+markers",
                name=sport_name,
                line=dict(color=SPORT_COLORS[sport_name], width=3),
                marker=dict(size=7, color=SPORT_COLORS[sport_name]),
                hovertemplate=(
                    f"Sport: {sport_name}<br>"
                    "Année: %{x}<br>"
                    f"{label}: %{{y:.2f}}<extra></extra>"
                ),
            )
        )

    fig = apply_common_layout(
        fig,
        title=f"Évolution temporelle de {label.lower()}",
        x_title="Année (Jeux Olympiques d’hiver)",
        y_title=label,
    )
    fig.update_xaxes(dtick=4)
    return fig



# Layout

def create_viz1_layout(prefix: str = "viz1") -> html.Section:
    return html.Section(
        className="section-block",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H2("Facteurs physiologiques et performance olympique"),
                    html.P(
                        "Explorer l’effet de l’âge, de la taille et du poids "
                        "selon les disciplines et les performances observées."
                    ),
                ],
            ),

            html.Div(
                className="filters-zone",
                children=[
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Sexe"),
                            dcc.Dropdown(
                                id=_id(prefix, "sex-filter"),
                                options=SEX_OPTIONS,
                                value="All",
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Médailles"),
                            dcc.Dropdown(
                                id=_id(prefix, "medal-filter"),
                                options=MEDAL_FILTER_OPTIONS,
                                value="All",
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Variable"),
                            dcc.Dropdown(
                                id=_id(prefix, "variable-filter"),
                                options=VARIABLE_OPTIONS,
                                value="age",
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Sport du nuage de points"),
                            dcc.Dropdown(
                                id=_id(prefix, "scatter-sport-filter"),
                                options=SPORT_OPTIONS,
                                value="All",
                                clearable=False,
                            ),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="physio-grid",
                children=[
                    html.Article(
                        className="viz-card",
                        children=[
                            html.Div(
                                className="viz-card-header",
                                children=[
                                    html.H3("Distribution"),
                                    html.P("Comparer les profils physiologiques selon les disciplines."),
                                ],
                            ),
                            dcc.Graph(
                                id=_id(prefix, "boxplot"),
                                config={"displayModeBar": False},
                                style={"height": "420px"},
                            ),
                        ],
                    ),
                    html.Article(
                        className="viz-card",
                        children=[
                            html.Div(
                                className="viz-card-header",
                                children=[
                                    html.H3("Relation taille / poids"),
                                    html.P("Observer les regroupements selon le sport et les médailles."),
                                ],
                            ),
                            dcc.Graph(
                                id=_id(prefix, "scatter"),
                                config={"displayModeBar": False},
                                style={"height": "420px"},
                            ),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="single-chart-row",
                children=[
                    html.Article(
                        className="viz-card viz-card-large",
                        children=[
                            html.Div(
                                className="viz-card-header",
                                children=[
                                    html.H3("Évolution temporelle"),
                                    html.P("Suivre la moyenne de la variable choisie dans le temps."),
                                ],
                            ),
                            dcc.Graph(
                                id=_id(prefix, "trend"),
                                config={"displayModeBar": False},
                                style={"height": "380px"},
                            ),
                        ],
                    )
                ],
            ),
        ],
    )



# Callbacks 

def register_viz1_callbacks(app: Dash, df: pd.DataFrame, prefix: str = "viz1") -> None:
    @app.callback(
        Output(_id(prefix, "boxplot"), "figure"),
        Output(_id(prefix, "scatter"), "figure"),
        Output(_id(prefix, "trend"), "figure"),
        Input(_id(prefix, "sex-filter"), "value"),
        Input(_id(prefix, "medal-filter"), "value"),
        Input(_id(prefix, "variable-filter"), "value"),
        Input(_id(prefix, "scatter-sport-filter"), "value"),
    )
    def update_viz1(selected_sex, selected_medal_filter, variable_key, selected_scatter_sport):
        dff = apply_global_filters(
            df=df,
            selected_sex=selected_sex,
            selected_medal_filter=selected_medal_filter,
        )

        fig_box = make_boxplot_figure(dff, variable_key=variable_key)
        fig_scatter = make_scatter_figure(dff, selected_sport=selected_scatter_sport)
        fig_trend = make_trend_figure(dff, variable_key=variable_key)

        return fig_box, fig_scatter, fig_trend





if __name__ == "__main__":
    df_test = load_and_preprocess_data(
        event_results_path="data/Olympic_Athlete_Event_Results.csv",
        athlete_bio_path="data/Olympic_Athlete_Bio.csv",
        games_path="data/Olympics_Games.csv",
    )

    app = Dash(__name__)
    app.layout = html.Div(
        style={
            "maxWidth": "1400px",
            "margin": "0 auto",
            "padding": "24px",
            "backgroundColor": "#0f1115",
            "minHeight": "100vh",
        },
        children=[create_viz1_layout(prefix="viz1")],
    )

    register_viz1_callbacks(app, df_test, prefix="viz1")
    app.run(debug=True)