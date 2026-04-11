"""INF8808 — Utilitaires partagés entre viz1 et viz2."""

import pandas as pd
import plotly.graph_objects as go


# Sports couverts
SELECTED_SPORTS = ["Biathlon", "Hockey sur glace", "Patinage de vitesse"]
ENGLISH_SPORTS_FILTER = ["Biathlon", "Ice Hockey", "Speed Skating"]

# Tables de traduction anglais → français
SPORT_TRANSLATIONS = {
    "Ice Hockey": "Hockey sur glace",
    "Speed Skating": "Patinage de vitesse",
}
MEDAL_TRANSLATIONS = {
    "Gold": "Or",
    "Silver": "Argent",
    "Bronze": "Bronze",
    "None": "Aucune",
}


def _id(prefix: str, name: str) -> str:
    """Génère un identifiant Dash de composant préfixé."""
    return f"{prefix}-{name}"


def _validate_columns(df: pd.DataFrame, required: list[str], df_name: str) -> None:
    """Lève une ValueError si des colonnes requises sont absentes du DataFrame."""
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {df_name}: {sorted(missing)}")


def make_empty_figure(message: str) -> go.Figure:
    """Retourne une figure Plotly vide affichant un message centré."""
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
