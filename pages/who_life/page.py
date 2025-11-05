from dash import html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
from utils.loaders import get_who
from . import ids

def _safe_kpi(df: pd.DataFrame):
    if "Life expectancy" in df and len(df):
        try:
            return round(pd.to_numeric(df["Life expectancy"], errors="coerce").mean(), 1)
        except Exception:
            return "—"
    return "—"

def layout():
    df = get_who()
    # listes tolérantes
    countries = sorted(df["Country"].dropna().unique().tolist()) if "Country" in df else []
    default = countries[:1] if countries else []
    kpi_value = _safe_kpi(df)

    # figure par défaut (évite une erreur au premier rendu)
    fig = px.scatter(title="Sélectionnez des pays pour afficher la tendance")

    return html.Div([
        html.H2("Life Expectancy — WHO"),
        html.Div(className="card", children=[
            html.H4("Espérance de vie moyenne (ans)"),
            html.H1(kpi_value, id=ids.KPI_LIFE, style={"margin": 0})
        ]),
        dcc.Dropdown(countries, default, id=ids.DROPDOWN_COUNTRY, multi=True, placeholder="Choisir des pays…"),
        dcc.Graph(id=ids.GRAPH_TRENDS, figure=fig)
    ])

@callback(Output(ids.GRAPH_TRENDS, "figure"),
          Input(ids.DROPDOWN_COUNTRY, "value"))
def update_trend(selected):
    df = get_who()
    if not selected:
        return px.scatter(title="Sélectionnez au moins un pays")
    needed = {"Country", "Year", "Life expectancy"}
    if not needed.issubset(set(df.columns)):
        return px.scatter(title="Colonnes manquantes : Country, Year, Life expectancy")
    dff = df[df["Country"].isin(selected)].copy()
    # assure types
    dff["Year"] = pd.to_numeric(dff["Year"], errors="coerce")
    dff["Life expectancy"] = pd.to_numeric(dff["Life expectancy"], errors="coerce")
    dff = dff.dropna(subset=["Year", "Life expectancy"])
    try:
        fig = px.line(dff, x="Year", y="Life expectancy", color="Country", markers=True,
                      title="Évolution de l’espérance de vie")
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        return fig
    except Exception as e:
        return px.scatter(title=f"Erreur: {e}")
