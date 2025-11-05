from dash import html, dcc, Input, Output, callback
import dash
import pandas as pd
import plotly.express as px
from pathlib import Path

dash.register_page(__name__, path="/life", name="Life (WHO)")

DATA = Path("data/clean/who_life_clean.csv")
DF = pd.read_csv(DATA) if DATA.exists() else pd.DataFrame(columns=["Country","Year","Life expectancy"])

def layout():
    countries = sorted(DF["Country"].unique().tolist()) if not DF.empty else []
    default = countries[:2] if len(countries) >= 2 else countries
    y_min = int(pd.to_numeric(DF["Year"], errors="coerce").min()) if "Year" in DF else 1990
    y_max = int(pd.to_numeric(DF["Year"], errors="coerce").max()) if "Year" in DF else 2015

    return html.Div([
        html.H2("Life Expectancy — WHO"),
        html.Div(className="card", children=[
            html.P("Sélectionnez des pays et une période pour visualiser l’évolution de l’espérance de vie."),
            dcc.Dropdown(countries, default, id="life-country", multi=True, placeholder="Choisir des pays…"),
            dcc.RangeSlider(y_min, y_max, value=[y_min, y_max], id="life-year",
                            marks={y_min:str(y_min), y_max:str(y_max)})
        ]),
        dcc.Graph(id="life-fig")
    ])

@callback(Output("life-fig","figure"),
          Input("life-country","value"),
          Input("life-year","value"))
def update_life(countries, yr):
    if DF.empty or not countries:
        return px.scatter(title="Données indisponibles ou aucun pays sélectionné")
    dff = DF[DF["Country"].isin(countries)].copy()
    dff["Year"] = pd.to_numeric(dff["Year"], errors="coerce")
    dff["Life expectancy"] = pd.to_numeric(dff["Life expectancy"], errors="coerce")
    dff = dff[(dff["Year"]>=yr[0]) & (dff["Year"]<=yr[1])]
    fig = px.line(dff, x="Year", y="Life expectancy", color="Country", markers=True,
                  title="Évolution de l’espérance de vie")
    fig.update_layout(margin=dict(l=20,r=20,t=40,b=20))
    return fig
