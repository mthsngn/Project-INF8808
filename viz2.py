import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback_context


# Configuration
SELECTED_SPORTS = ["Biathlon", "Ice Hockey", "Speed Skating"]

SPORT_OPTIONS = [
    {"label": "Tous",          "value": "All"},
    {"label": "Biathlon",      "value": "Biathlon"},
    {"label": "Ice Hockey",    "value": "Ice Hockey"},
    {"label": "Speed Skating", "value": "Speed Skating"},
]

MEDAL_ORDER  = ["Gold", "Silver", "Bronze"]
MEDAL_COLORS = {"Gold": "#D4AF37", "Silver": "#C0C0C0", "Bronze": "#CD7F32"}

# Noms complets des pays à partir de leur code NOC
COUNTRY_NAMES = {
    "CAN": "Canada",          "USA": "États-Unis",        "FRA": "France",
    "NOR": "Norvège",         "SWE": "Suède",             "FIN": "Finlande",
    "GER": "Allemagne",       "ITA": "Italie",            "JPN": "Japon",
    "CHN": "Chine",           "KOR": "Corée du Sud",      "SUI": "Suisse",
    "GBR": "Royaume-Uni",     "AUT": "Autriche",          "NED": "Pays-Bas",
    "RUS": "Russie",          "URS": "URSS",              "EUN": "Éq. Unifiée",
    "ROC": "Comité Olympique Russe",
    "UKR": "Ukraine",         "BLR": "Biélorussie",       "KAZ": "Kazakhstan",
    "CZE": "Rép. Tchèque",    "SVK": "Slovaquie",         "POL": "Pologne",
    "HUN": "Hongrie",         "SLO": "Slovénie",          "CRO": "Croatie",
    "EST": "Estonie",         "LAT": "Lettonie",          "LTU": "Lituanie",
    "DEN": "Danemark",        "BEL": "Belgique",          "LIE": "Liechtenstein",
    "MON": "Monaco",          "BUL": "Bulgarie",          "ROU": "Roumanie",
    "GRE": "Grèce",           "ESP": "Espagne",
    "NZL": "Nouvelle-Zélande","AUS": "Australie",
    "MGL": "Mongolie",        "GDR": "Allemagne Est",     "TCH": "Tchécoslovaquie",
    "YUG": "Yougoslavie",     "FRG": "Allemagne Ouest",   "BIH": "Bosnie-Herzégovine",
}

# Coordonnées des centroides approximatifs des pays (pour placer les bulles dans la vue continent)
COUNTRY_COORDS = {
    "CAN": (56.13, -106.35), "USA": (37.09,  -95.71),
    "NOR": (60.47,    8.47), "SWE": (60.13,   18.64), "FIN": (61.92,  25.75),
    "GER": (51.17,   10.45), "AUT": (47.52,   14.55), "SUI": (46.82,   8.23),
    "FRA": (46.23,    2.21), "ITA": (41.87,   12.57), "GBR": (55.38,  -3.44),
    "NED": (52.13,    5.29), "DEN": (56.26,    9.50), "BEL": (50.50,   4.47),
    "LIE": (47.17,    9.56), "MON": (43.74,    7.42), "BUL": (42.73,  25.49),
    "ROU": (45.94,   24.97), "GRE": (39.07,   21.82), "ESP": (40.46,  -3.75),
    "CZE": (49.82,   15.47), "SVK": (48.67,   19.70), "POL": (51.92,  19.15),
    "HUN": (47.16,   19.50), "SLO": (46.15,   14.99), "CRO": (45.10,  15.20),
    "EST": (58.60,   25.01), "LAT": (56.88,   24.60), "LTU": (55.17,  23.88),
    "GDR": (52.52,   13.41), "TCH": (50.08,   14.44), "YUG": (44.02,  21.01),
    "FRG": (51.17,   10.45), "BIH": (43.92,   17.68),
    "RUS": (61.52,  105.32), "URS": (55.76,   37.62), "EUN": (55.00,  50.00),
    "ROC": (55.76,   37.62), "UKR": (48.38,   31.17), "BLR": (53.71,  27.95),
    "KAZ": (48.02,   66.92),
    "JPN": (36.20,  138.25), "KOR": (35.91,  127.77), "CHN": (35.86, 104.20),
    "MGL": (46.86,  103.85),
    "AUS": (-25.27, 133.78), "NZL": (-40.90, 174.89),
}

# Continents
CONTINENTS: dict[str, dict] = {
    "Amérique du Nord": {
        "nocs"      : ["CAN", "USA", "MEX"],
        "color"     : "#4A90D9",   # couleur de la bordure
        "lat_range" : [15, 80],
        "lon_range" : [-170, -50],
        "center"    : (52, -100),
    },
    "Europe": {
        "nocs": [
            "NOR", "SWE", "FIN", "GER", "AUT", "SUI", "FRA", "ITA", "GBR",
            "NED", "CZE", "SVK", "POL", "HUN", "SLO", "CRO", "EST", "LAT",
            "LTU", "DEN", "BEL", "LIE", "MON", "BUL", "ROU", "GRE", "ESP",
            "FRG", "GDR", "TCH", "YUG", "BIH",
        ],
        "color"    : "#E8A838",
        "lat_range": [35, 72],
        "lon_range": [-12, 42],
        "center"   : (55, 12),
    },
    "Russie / ex-URSS": {
        "nocs"     : ["RUS", "URS", "EUN", "ROC", "UKR", "BLR", "KAZ"],
        "color"    : "#E85C5C",
        "lat_range": [40, 80],
        "lon_range": [18, 180],
        "center"   : (62, 90),
    },
    "Asie": {
        "nocs"     : ["JPN", "KOR", "CHN", "MGL"],
        "color"    : "#5CBF85",
        "lat_range": [10, 55],
        "lon_range": [70, 155],
        "center"   : (35, 115),
    },
    "Océanie": {
        "nocs"     : ["AUS", "NZL"],
        "color"    : "#1ABC9C",
        "lat_range": [-50, -5], 
        "lon_range": [110, 180],
        "center"   : (-30, 145),
    },
}

# Mapping inverse NOC dans CONTINENTS pour faciliter lecture du continent dans le callback de la carte
NOC_TO_CONTINENT: dict[str, str] = {}
for _cont, _conf in CONTINENTS.items():
    for _noc in _conf["nocs"]:
        NOC_TO_CONTINENT[_noc] = _cont


# Styles du bouton Retour
_BTN_BASE = {
    "display"      : "inline-flex",
    "alignItems"   : "center",
    "gap"          : "6px",
    "padding"      : "6px 16px",
    "background"   : "var(--accent, #d8b56a)",
    "color"        : "#161616",
    "border"       : "none",
    "borderRadius" : "8px",
    "fontSize"     : "0.88rem",
    "fontWeight"   : "700",
    "cursor"       : "pointer",
    "fontFamily"   : "Inter, Arial, sans-serif",
    "boxShadow"    : "0 4px 12px rgba(216,181,106,0.25)",
    "marginLeft"   : "auto",
}
BTN_HIDDEN  = {**_BTN_BASE, "display": "none"}
BTN_VISIBLE = {
    **_BTN_BASE,
    "position" : "absolute",
    "top"      : "63px",
    "left"    : "250px",
    "zIndex"   : "10",
}


# Helpers

def _id(prefix: str, name: str) -> str:
    return f"{prefix}-{name}"


def _validate_columns(df: pd.DataFrame, required: list[str], name: str) -> None:
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {name}: {sorted(missing)}")


def _geo_layout(fig: go.Figure, lat_range=None, lon_range=None, title: str = "") -> go.Figure:
    """Applique un layout geo commun."""
    geo = dict(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#CBD5E1",
        showcountries=True,
        countrycolor="#E2E8F0",
        showland=True,
        landcolor="#F1F5F9",
        showocean=True,
        oceancolor="#DBEAFE",
        showlakes=True,
        lakecolor="#DBEAFE",
        bgcolor="rgba(0,0,0,0)",
    )
    if lat_range:
        geo["lataxis_range"]  = lat_range
        geo["lonaxis_range"]  = lon_range
        geo["projection_type"] = "mercator"

    fig.update_layout(
        title=dict(
            text=title, x=0.02, xanchor="left",
            font=dict(size=14, color="#1F2937", family="Inter, Arial, sans-serif"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0),
        geo=geo,
        showlegend=False,
        font=dict(family="Inter, Arial, sans-serif", color="#1F2937"),
    )
    return fig


def make_empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[dict(
            text=message, x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=15, color="#6B7280"),
        )],
    )
    return fig


def apply_common_layout(
    fig: go.Figure, title: str, x_title: str = "", y_title: str = ""
) -> go.Figure:
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
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1.0, bgcolor="rgba(0,0,0,0)",
        ),
    )
    fig.update_xaxes(showline=True, linecolor="#D1D5DB", gridcolor="#E5E7EB", zeroline=False)
    fig.update_yaxes(showline=True, linecolor="#D1D5DB", gridcolor="#E5E7EB", zeroline=False)
    return fig


def get_country_label(code: str) -> str:
    if pd.isna(code):
        return "Unknown"
    return COUNTRY_NAMES.get(str(code).strip().upper(), str(code).strip().upper())


# Chargement et prétraitement

def load_and_preprocess_data(event_results_path: str) -> pd.DataFrame:
    df = pd.read_csv(event_results_path)
    _validate_columns(df, ["sport", "medal", "country_noc"], "event_results")

    optional = ["athlete", "athlete_id", "edition_id", "event", "result_id"]
    keep = ["sport", "medal", "country_noc"] + [c for c in optional if c in df.columns]

    df = df[keep].copy()
    df = df[df["sport"].isin(SELECTED_SPORTS)].copy()
    df = df.dropna(subset=["sport", "country_noc"]).copy()

    df["country_noc"]  = df["country_noc"].astype(str).str.strip().str.upper()
    df["medal"]        = df["medal"].fillna("None").astype(str).str.strip().replace({"": "None"})
    df["country_name"] = df["country_noc"].map(get_country_label)

    # Identifiant de déduplication
    if "result_id" in df.columns:
        df["medal_unit_id"] = (
            df["sport"] + "|" + df["country_noc"] + "|" + df["medal"] + "|" + df["result_id"].astype(str)
        )
    elif {"edition_id", "event"}.issubset(df.columns):
        df["medal_unit_id"] = (
            df["sport"] + "|" + df["country_noc"] + "|" + df["medal"]
            + "|" + df["edition_id"].astype(str) + "|" + df["event"].astype(str)
        )
    elif "athlete_id" in df.columns:
        df["medal_unit_id"] = (
            df["sport"] + "|" + df["country_noc"] + "|" + df["medal"] + "|" + df["athlete_id"].astype(str)
        )
    else:
        df["medal_unit_id"] = df["sport"] + "|" + df["country_noc"] + "|" + df["medal"]

    return df


# Filtres et agrégations

def apply_sport_filter_for_medals(df: pd.DataFrame, selected_sport: str) -> pd.DataFrame:
    dff = df[df["medal"].isin(MEDAL_ORDER)].copy()
    if selected_sport != "All":
        dff = dff[dff["sport"] == selected_sport].copy()
    return dff


def aggregate_country_medals(df: pd.DataFrame, selected_sport: str) -> pd.DataFrame:
    dff = apply_sport_filter_for_medals(df, selected_sport)
    if dff.empty:
        return pd.DataFrame(columns=["country_noc", "country_name", "medal", "count"])
    dff = dff[["country_noc", "country_name", "medal", "medal_unit_id"]].drop_duplicates()
    return (
        dff.groupby(["country_noc", "country_name", "medal"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )


# Figures carte

def make_world_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:

    agg = aggregate_country_medals(df, selected_sport)

    # Totaux par continent
    country_totals = (
        agg.groupby("country_noc", as_index=False)["count"]
        .sum().rename(columns={"count": "medals"})
    )
    country_totals["continent"] = country_totals["country_noc"].map(NOC_TO_CONTINENT)
    cont_totals = (
        country_totals.dropna(subset=["continent"])
        .groupby("continent", as_index=False)["medals"].sum()
    )
    cont_medal_dict = dict(zip(cont_totals["continent"], cont_totals["medals"]))

    max_medals = max(cont_medal_dict.values()) if cont_medal_dict else 1

    pink_scale = [
        [0.0, "#fde0ef"],
        [0.25, "#f9b3d4"],
        [0.55, "#f57ab4"],
        [0.78, "#c51b8a"],
        [1.0,  "#7a0177"],
    ]

    fig = go.Figure()

    # Une trace Choropleth par continent :
    for cont_name, conf in CONTINENTS.items():
        total = cont_medal_dict.get(cont_name, 0)
        nocs  = conf["nocs"]

        fig.add_trace(go.Choropleth(
            locations         = nocs,
            z                 = [total] * len(nocs),
            zmin              = 0,
            zmax              = max_medals,
            locationmode      = "ISO-3",
            colorscale        = pink_scale,
            showscale         = False,
            marker_line_color = conf["color"],  # bordure couleur du continent
            marker_line_width = 0.5,
            customdata        = [cont_name] * len(nocs),
            hovertemplate     = (
                f"<b>{cont_name}</b><br>"
                f"Médailles totales : {total}<br>"
                "<i>Cliquez pour explorer</i>"
                "<extra></extra>"
            ),
            name = cont_name,
        ))

    # Labels texte au centre de chaque continent
    for cont_name, conf in CONTINENTS.items():
        total      = cont_medal_dict.get(cont_name, 0)
        clat, clon = conf["center"]
        fig.add_trace(go.Scattergeo(
            lat       = [clat],
            lon       = [clon],
            mode      = "text",
            text      = [f"<b>{cont_name}</b><br>{total} médailles"],
            textfont  = dict(size=10, color="black", family="Inter, Arial, sans-serif"),
            hoverinfo = "skip",
            showlegend = False,
            name      = f"_label_{cont_name}",
        ))

    title = "Carte des médailles par continent"
    if selected_sport != "All":
        title += f" : {selected_sport}"

    fig = _geo_layout(fig, title=title)

    # Une seule colorbar sur la première trace, cachée sur les autres
    fig.data[0].update(
        showscale=True,
        colorbar=dict(
            title    = dict(text="Médailles", font=dict(size=12, color="#1F2937")),
            thickness= 12,
            len      = 0.55,
            tickfont = dict(size=10, color="#1F2937"),
        ),
    )
    for trace in fig.data[1:]:
        if hasattr(trace, "showscale"):
            trace.showscale = False
    fig.update_layout(showlegend=False)

    return fig


def make_bubble_figure(
    df: pd.DataFrame,
    selected_sport: str,
    continent: str,
) -> go.Figure:
    """
    Vue continent : scatter_geo bubble map.
    Taille bulle = total médailles.  Couleur = total médailles.
    Hover = détail or / argent / bronze.
    """
    if continent not in CONTINENTS:
        return make_empty_figure(f"Continent inconnu : {continent}")

    conf = CONTINENTS[continent]
    agg  = aggregate_country_medals(df, selected_sport)
    agg  = agg[agg["country_noc"].isin(conf["nocs"])].copy()

    if agg.empty:
        return make_empty_figure(f"Aucune médaille pour {continent}.")

    # Pivot pour avoir or/argent/bronze par pays
    pivot = (
        agg.pivot_table(
            index="country_noc", columns="medal",
            values="count", fill_value=0,
        )
        .reset_index()
    )
    for m in MEDAL_ORDER:
        if m not in pivot.columns:
            pivot[m] = 0
    pivot["total"]        = pivot[MEDAL_ORDER].sum(axis=1)
    pivot["country_name"] = pivot["country_noc"].map(lambda x: COUNTRY_NAMES.get(x, x))
    pivot["lat"]          = pivot["country_noc"].map(lambda x: COUNTRY_COORDS.get(x, (0, 0))[0])
    pivot["lon"]          = pivot["country_noc"].map(lambda x: COUNTRY_COORDS.get(x, (0, 0))[1])
    pivot = pivot[pivot["total"] > 0].copy()

    if pivot.empty:
        return make_empty_figure(f"Aucune médaille pour {continent}.")

    # Taille des bulles
    max_t = pivot["total"].max()
    pivot["size"] = 18 + (pivot["total"] / max_t) * 37

    # Échelle de couleur rose
    pink_scale = [
        [0.0, "#fde0ef"], [0.25, "#f9b3d4"],
        [0.55, "#f57ab4"], [0.78, "#c51b8a"],
        [1.0,  "#7a0177"],
    ]

    fig = go.Figure()

    fig.add_trace(go.Scattergeo(
        lat        = pivot["lat"],
        lon        = pivot["lon"],
        mode       = "markers+text",
        marker     = dict(
            size       = pivot["size"],
            color      = pivot["total"],
            colorscale = pink_scale,
            showscale  = True,
            colorbar   = dict(
                title      = dict(text="Médailles", font=dict(size=12, color="#1F2937")),
                thickness  = 12,
                len        = 0.55,
                tickfont   = dict(size=11, color="#1F2937"),
            ),
            line       = dict(color="white", width=1.5),
            opacity    = 0.88,
        ),
        text          = pivot["country_name"],
        textposition  = "top center",
        textfont      = dict(size=10, color="#1F2937"),
        customdata    = pivot[["Gold", "Silver", "Bronze", "total", "country_name"]].values,
        hovertemplate = (
            "<b>%{customdata[4]}</b><br>"
            "🥇 Or : %{customdata[0]}<br>"
            "🥈 Argent : %{customdata[1]}<br>"
            "🥉 Bronze : %{customdata[2]}<br>"
            "<b>Total : %{customdata[3]}</b>"
            "<extra></extra>"
        ),
        name = "Pays",
    ))

    title = f"Médailles : {continent}"
    if selected_sport != "All":
        title += f"  ·  {selected_sport}"

    fig = _geo_layout(
        fig,
        lat_range = conf["lat_range"],
        lon_range = conf["lon_range"],
        title     = title,
    )

    return fig


# Figure bar chart

def make_barchart_figure(df: pd.DataFrame, selected_sport: str) -> go.Figure:
    agg = aggregate_country_medals(df, selected_sport)

    if agg.empty:
        return make_empty_figure("Aucune médaille disponible pour ce graphique.")

    totals = (
        agg.groupby(["country_noc", "country_name"], as_index=False)["count"]
        .sum().rename(columns={"count": "total_medals"})
    )
    country_order = (
        totals.sort_values(["total_medals", "country_name"], ascending=[False, True])
        ["country_noc"].tolist()
    )
    all_countries = totals[["country_noc", "country_name"]].drop_duplicates()

    full_index = pd.MultiIndex.from_product(
        [country_order, MEDAL_ORDER], names=["country_noc", "medal"]
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
        agg_full["country_noc"], categories=country_order, ordered=True
    )
    agg_full = agg_full.sort_values(["country_noc", "medal"])

    fig = go.Figure()
    for medal in MEDAL_ORDER:
        dm = agg_full[agg_full["medal"] == medal]
        fig.add_trace(go.Bar(
            x         = dm["country_name"],
            y         = dm["count"],
            name      = medal,
            marker_color = MEDAL_COLORS[medal],
            customdata = dm[["country_noc", "total_medals"]],
            hovertemplate = (
                "<b>%{x}</b><br>"
                f"Type : {medal}<br>"
                "Nombre : %{y}<br>"
                "Total pays : %{customdata[1]}<extra></extra>"
            ),
        ))

    title = "Distribution des médailles par pays"
    if selected_sport != "All":
        title += f" : {selected_sport}"

    fig = apply_common_layout(fig, title=title, x_title="Pays", y_title="Nombre de médailles")
    fig.update_layout(
        barmode="group", bargap=0.18, bargroupgap=0.08,
        legend_title_text="Type de médaille",
    )
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=11), automargin=True)
    fig.update_yaxes(tickfont=dict(size=11), rangemode="tozero")
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
                        "Cliquez sur un continent pour explorer les pays médaillés "
                        "dans cette région. Utilisez le filtre de sport pour affiner l'analyse."
                    ),
                ],
            ),

            # Filtre sport
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

            # Store pour mémoriser le continent actif (None = vue monde)
            dcc.Store(id=_id(prefix, "continent-store"), data=None),

            html.Div(
                className="geo-grid",
                children=[
                    # Bar chart
                    html.Article(
                        className="viz-card",
                        children=[
                            html.Div(
                                className="viz-card-header",
                                children=[
                                    html.H3("Distribution des médailles par pays"),
                                    html.P("Comparer le nombre de médailles d'or, d'argent et de bronze."),
                                ],
                            ),
                            dcc.Graph(
                                id=_id(prefix, "bar"),
                                config={"displayModeBar": False},
                                style={"height": "460px"},
                            ),
                        ],
                    ),

                    # Carte interactive
                    html.Article(
                        className="viz-card viz-card-map",
                        children=[
                            html.Div(
                                className="viz-card-header",
                                children=[
                                    html.H3("Carte géographique des médailles"),
                                    html.P(
                                        id=_id(prefix, "map-subtitle"),
                                        children="Cliquez sur un continent pour plus de détails.",
                                    ),
                                ],
                            ),
                            # Conteneur relatif pour positionner le bouton par-dessus la carte
                            html.Div(
                                style={"position": "relative"},
                                children=[
                                    dcc.Graph(
                                        id=_id(prefix, "map"),
                                        config={"displayModeBar": False},
                                        style={"height": "500px"},
                                    ),
                                    # Bouton retour en overlay haut-droite de la carte
                                    html.Button(
                                        "← Retour",
                                        id=_id(prefix, "back-btn"),
                                        n_clicks=0,
                                        style=BTN_HIDDEN,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# Callbacks

def register_viz2_callbacks(app: Dash, df: pd.DataFrame, prefix: str = "viz2") -> None:

    # Callback barchart
    @app.callback(
        Output(_id(prefix, "bar"), "figure"),
        Input(_id(prefix, "sport-filter"), "value"),
    )
    def update_bar(selected_sport):
        return make_barchart_figure(df, selected_sport)

    # Callback carte (drill-down continent)
    @app.callback(
        Output(_id(prefix, "map"),             "figure"),
        Output(_id(prefix, "continent-store"), "data"),
        Output(_id(prefix, "back-btn"),        "style"),
        Output(_id(prefix, "map-subtitle"),    "children"),
        Input(_id(prefix, "sport-filter"), "value"),
        Input(_id(prefix, "map"),          "clickData"),
        Input(_id(prefix, "back-btn"),     "n_clicks"),
        State(_id(prefix, "continent-store"), "data"),
        prevent_initial_call=False,
    )
    def update_map(selected_sport, click_data, back_clicks, current_continent):
        triggered  = callback_context.triggered
        triggered_id = triggered[0]["prop_id"].split(".")[0] if triggered else None

        #  Retour vers la vue monde
        if triggered_id == _id(prefix, "back-btn"):
            return (
                make_world_figure(df, selected_sport),
                None,
                BTN_HIDDEN,
                "Cliquez sur un continent pour plus de détails.",
            )

        # Clic sur la carte
        if triggered_id == _id(prefix, "map") and click_data:
            try:
                point = click_data["points"][0]

                raw = point.get("customdata")
                continent = raw if isinstance(raw, str) and raw in CONTINENTS else None

                if continent is None:
                    loc = point.get("location", "")
                    continent = NOC_TO_CONTINENT.get(str(loc).upper())
            except Exception:
                continent = None

            if continent:
                subtitle = f"Vue détaillée : {continent}. Cliquez sur « Retour » pour la vue monde."
                return (
                    make_bubble_figure(df, selected_sport, continent),
                    continent,
                    BTN_VISIBLE,
                    subtitle,
                )

            # Clic sur océan ou zone sans données
            if current_continent:
                subtitle = f"Vue détaillée : {current_continent}. Cliquez sur « Retour » pour la vue monde."
                return (
                    make_bubble_figure(df, selected_sport, current_continent),
                    current_continent,
                    BTN_VISIBLE,
                    subtitle,
                )
            return (
                make_world_figure(df, selected_sport),
                None,
                BTN_HIDDEN,
                "Cliquez sur un continent pour plus de détails.",
            )

        # Changement de sport
        if current_continent:
            subtitle = f"Vue détaillée : {current_continent}. Cliquez sur « Retour » pour la vue monde."
            return (
                make_bubble_figure(df, selected_sport, current_continent),
                current_continent,
                BTN_VISIBLE,
                subtitle,
            )

        # Vue par défaut (monde)
        return (
            make_world_figure(df, selected_sport),
            None,
            BTN_HIDDEN,
            "Cliquez sur un continent pour plus de détails.",
        )


if __name__ == "__main__":
    df_test = load_and_preprocess_data(
        event_results_path="data/Olympic_Athlete_Event_Results.csv"
    )

    app = Dash(__name__)
    app.layout = html.Div(
        style={
            "maxWidth": "1400px",
            "margin" : "0 auto",
            "padding": "24px",
            "backgroundColor": "#0f1115",
            "minHeight": "100vh",
        },
        children=[create_viz2_layout(prefix="viz2")],
    )

    register_viz2_callbacks(app, df_test, prefix="viz2")
    app.run(debug=True)