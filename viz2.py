"""
INF8808
Exécution :
    pip install dash pandas numpy plotly
    python viz2.py
"""

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


# Configuration
SELECTED_SPORTS = ["Biathlon", "Ice Hockey", "Speed Skating"]

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

COUNTRY_NAMES = {
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
        margin=dict(l=55, r=25, t=60, b=60),
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


def get_country_label(code: str) -> str:
    if pd.isna(code):
        return "Unknown"
    code = str(code).strip().upper()
    return COUNTRY_NAMES.get(code, code)



# Chargement et prétraitement

def load_and_preprocess_data(event_results_path: str) -> pd.DataFrame:
    df = pd.read_csv(event_results_path)

    _validate_columns(
        df,
        ["sport", "medal", "country_noc"],
        "event_results",
    )

    optional_columns = [
        "athlete",
        "athlete_id",
        "edition_id",
        "event",
        "result_id",
    ]

    keep_columns = ["sport", "medal", "country_noc"] + [
        col for col in optional_columns if col in df.columns
    ]

    df = df[keep_columns].copy()
    df = df[df["sport"].isin(SELECTED_SPORTS)].copy()
    df = df.dropna(subset=["sport", "country_noc"]).copy()

    df["country_noc"] = df["country_noc"].astype(str).str.strip().str.upper()
    df["medal"] = df["medal"].fillna("None").astype(str).str.strip()
    df["medal"] = df["medal"].replace({"": "None"})
    df["country_name"] = df["country_noc"].map(get_country_label)

    # Identifiant d'unité de médaille pour éviter le surcomptage
    if "result_id" in df.columns:
        df["medal_unit_id"] = (
            df["sport"].astype(str)
            + "|"
            + df["country_noc"].astype(str)
            + "|"
            + df["medal"].astype(str)
            + "|"
            + df["result_id"].astype(str)
        )
    elif {"edition_id", "event"}.issubset(df.columns):
        df["medal_unit_id"] = (
            df["sport"].astype(str)
            + "|"
            + df["country_noc"].astype(str)
            + "|"
            + df["medal"].astype(str)
            + "|"
            + df["edition_id"].astype(str)
            + "|"
            + df["event"].astype(str)
        )
    elif "athlete_id" in df.columns:
        df["medal_unit_id"] = (
            df["sport"].astype(str)
            + "|"
            + df["country_noc"].astype(str)
            + "|"
            + df["medal"].astype(str)
            + "|"
            + df["athlete_id"].astype(str)
        )
    else:
        df["medal_unit_id"] = (
            df["sport"].astype(str)
            + "|"
            + df["country_noc"].astype(str)
            + "|"
            + df["medal"].astype(str)
        )

    return df



# Filtres

def apply_sport_filter_for_medals(df: pd.DataFrame, selected_sport: str) -> pd.DataFrame:
    dff = df[df["medal"].isin(MEDAL_ORDER)].copy()

    if selected_sport != "All":
        dff = dff[dff["sport"] == selected_sport].copy()

    return dff



# Agrégation

def aggregate_country_medals(df: pd.DataFrame, selected_sport: str) -> pd.DataFrame:
    dff = apply_sport_filter_for_medals(df, selected_sport)

    if dff.empty:
        return pd.DataFrame(columns=["country_noc", "country_name", "medal", "count"])

    dff = dff[["country_noc", "country_name", "medal", "medal_unit_id"]].drop_duplicates().copy()

    agg = (
        dff.groupby(["country_noc", "country_name", "medal"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )

    return agg



# Figures

def make_choropleth_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:
    agg = aggregate_country_medals(df, selected_sport)

    if agg.empty:
        return make_empty_figure("Aucune médaille disponible pour cette carte.")

    totals = (
        agg.groupby(["country_noc", "country_name"], as_index=False)["count"]
        .sum()
        .rename(columns={"count": "medals"})
    )

    pink_scale = [
        [0.0, "#fde0ef"],
        [0.2, "#f9b3d4"],
        [0.4, "#f57ab4"],
        [0.6, "#e74a9e"],
        [0.8, "#c51b8a"],
        [1.0, "#7a0177"],
    ]

    max_z = max(1, int(totals["medals"].max()))

    fig = go.Figure(
        go.Choropleth(
            locations=totals["country_noc"],
            z=totals["medals"],
            locationmode="ISO-3",
            text=totals["country_name"],
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
        title += f" — {selected_sport}"

    fig.update_layout(
        title=dict(text=title, x=0.02, xanchor="left"),
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        geo=dict(
            projection_type="natural earth",
            showframe=False,
            showcoastlines=True,
            coastlinecolor="white",
            showcountries=True,
            countrycolor="white",
            showland=True,
            landcolor="#EAF1F8",
            showocean=True,
            oceancolor="#C7DFF2",
            showlakes=True,
            lakecolor="#C7DFF2",
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    return fig


def make_barchart_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:
    agg = aggregate_country_medals(df, selected_sport)

    if agg.empty:
        return make_empty_figure("Aucune médaille disponible pour ce graphique.")

    totals = (
        agg.groupby(["country_noc", "country_name"], as_index=False)["count"]
        .sum()
        .rename(columns={"count": "total_medals"})
    )

    country_order = (
        totals.sort_values(["total_medals", "country_name"], ascending=[False, True])["country_noc"]
        .tolist()
    )

    all_countries = totals[["country_noc", "country_name"]].drop_duplicates().copy()

    full_index = pd.MultiIndex.from_product(
        [country_order, MEDAL_ORDER],
        names=["country_noc", "medal"],
    )

    agg_full = (
        agg[["country_noc", "medal", "count"]]
        .set_index(["country_noc", "medal"])
        .reindex(full_index, fill_value=0)
        .reset_index()
    )

    agg_full = agg_full.merge(all_countries, on="country_noc", how="left")
    agg_full = agg_full.merge(totals, on=["country_noc", "country_name"], how="left")

    agg_full["country_noc"] = pd.Categorical(
        agg_full["country_noc"],
        categories=country_order,
        ordered=True,
    )
    agg_full = agg_full.sort_values(["country_noc", "medal"])

    fig = go.Figure()

    for medal in MEDAL_ORDER:
        dm = agg_full[agg_full["medal"] == medal].copy()

        fig.add_trace(
            go.Bar(
                x=dm["country_name"],
                y=dm["count"],
                name=medal,
                marker_color=MEDAL_COLORS[medal],
                customdata=dm[["country_noc", "total_medals"]],
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"Type: {medal}<br>"
                    "Nombre de médailles: %{y}<br>"
                    "Total du pays: %{customdata[1]}<extra></extra>"
                ),
            )
        )

    title = "Distribution des médailles par pays"
    if selected_sport != "All":
        title += f" — {selected_sport}"

    fig = apply_common_layout(
        fig,
        title=title,
        x_title="Pays",
        y_title="Nombre de médailles",
    )

    fig.update_layout(
        barmode="group",
        bargap=0.18,
        bargroupgap=0.08,
        legend_title_text="Type de médaille",
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



# Layout 

def create_viz2_layout(prefix: str = "viz2") -> html.Section:
    return html.Section(
        className="section-block",
        children=[
            html.Div(
                className="section-header",
                children=[
                    html.H2("Facteurs géographiques et performance olympique"),
                    html.P(
                        "Comparer les pays médaillés et visualiser leur répartition "
                        "géographique selon le sport sélectionné."
                    ),
                ],
            ),

            html.Div(
                className="filters-zone",
                children=[
                    html.Div(
                        className="filter-item",
                        children=[
                            html.Label("Sport"),
                            dcc.Dropdown(
                                id=_id(prefix, "sport-filter"),
                                options=SPORT_OPTIONS,
                                value="All",
                                clearable=False,
                            ),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="geo-grid",
                children=[
                    html.Article(
                        className="viz-card",
                        children=[
                            html.Div(
                                className="viz-card-header",
                                children=[
                                    html.H3("Distribution des médailles par pays"),
                                    html.P("Comparer le nombre de médailles d’or, d’argent et de bronze."),
                                ],
                            ),
                            dcc.Graph(
                                id=_id(prefix, "bar"),
                                config={"displayModeBar": False},
                                style={"height": "460px"},
                            ),
                        ],
                    ),
                    html.Article(
                        className="viz-card viz-card-map",
                        children=[
                            html.Div(
                                className="viz-card-header",
                                children=[
                                    html.H3("Carte géographique des médailles"),
                                    html.P("Observer les zones géographiques les plus représentées."),
                                ],
                            ),
                            dcc.Graph(
                                id=_id(prefix, "map"),
                                config={"displayModeBar": False},
                                style={"height": "500px"},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )



# Callbacks 

def register_viz2_callbacks(app: Dash, df: pd.DataFrame, prefix: str = "viz2") -> None:
    @app.callback(
        Output(_id(prefix, "map"), "figure"),
        Output(_id(prefix, "bar"), "figure"),
        Input(_id(prefix, "sport-filter"), "value"),
    )
    def update_viz2(selected_sport):
        fig_map = make_choropleth_figure(df, selected_sport=selected_sport)
        fig_bar = make_barchart_figure(df, selected_sport=selected_sport)
        return fig_map, fig_bar




if __name__ == "__main__":
    df_test = load_and_preprocess_data(
        event_results_path="data/Olympic_Athlete_Event_Results.csv"
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
        children=[create_viz2_layout(prefix="viz2")],
    )

    register_viz2_callbacks(app, df_test, prefix="viz2")
    app.run(debug=True)
