from dash import Dash, html
from viz1 import (
    load_and_preprocess_data as load_viz1_data,
    create_viz1_layout,
    register_viz1_callbacks,
)
from viz2 import (
    load_and_preprocess_data as load_viz2_data,
    create_viz2_layout,
    register_viz2_callbacks,
)


# Chargement des données

df_viz1 = load_viz1_data(
    "data/Olympic_Athlete_Event_Results.csv",
    "data/Olympic_Athlete_Bio.csv",
    "data/Olympics_Games.csv",
)

df_viz2 = load_viz2_data(
    "data/Olympic_Athlete_Event_Results.csv"
)


# KPI simples pour le haut de page

n_athletes = df_viz1["athlete_id"].nunique()
n_sports = df_viz1["sport"].nunique()
n_years = df_viz1["year"].nunique()
n_countries = df_viz1["country_noc"].nunique()


# App Dash

app = Dash(__name__)
app.title = "JO d'Hiver - Tableau de bord interactif"



# Layout principal

app.layout = html.Div(
    className="page-container",
    children=[
        # HEADER
        html.Header(
            className="header-zone",
            children=[
                html.Div(
                    className="header-content",
                    children=[
                        html.P("Visualisation de données", className="eyebrow"),
                        html.H1("Jeux Olympiques d'Hiver"),
                        html.P(
                            "Analyse des performances olympiques d'hiver selon les facteurs physiologiques et géographiques.",
                            className="header-description",
                        ),
                    ],
                )
            ],
        ),

        # KPI
        html.Section(
            className="kpi-row",
            children=[
                html.Article(
                    className="kpi-card",
                    children=[
                        html.Span("Athlètes", className="kpi-label"),
                        html.H2(f"{n_athletes:,}".replace(",", " "), className="kpi-value"),
                        html.P("Profils uniques recensés", className="kpi-note"),
                    ],
                ),
                html.Article(
                    className="kpi-card",
                    children=[
                        html.Span("Sports", className="kpi-label"),
                        html.H2(str(n_sports), className="kpi-value"),
                        html.P("Sports d’hiver analysés", className="kpi-note"),
                    ],
                ),
                html.Article(
                    className="kpi-card",
                    children=[
                        html.Span("Années", className="kpi-label"),
                        html.H2(str(n_years), className="kpi-value"),
                        html.P("Années couvertes", className="kpi-note"),
                    ],
                ),
                html.Article(
                    className="kpi-card",
                    children=[
                        html.Span("Pays", className="kpi-label"),
                        html.H2(str(n_countries), className="kpi-value"),
                        html.P("Pays représentés", className="kpi-note"),
                    ],
                ),
            ],
        ),

        # SECTION 1
        create_viz1_layout(prefix="viz1"),

        # SECTION 2
        create_viz2_layout(prefix="viz2"),
    ],
)


# Callbacks

register_viz1_callbacks(app, df_viz1, prefix="viz1")
register_viz2_callbacks(app, df_viz2, prefix="viz2")


# Run

if __name__ == "__main__":
    app.run(debug=True)