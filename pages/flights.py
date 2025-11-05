from dash import html, dcc
import dash
import pandas as pd
import plotly.express as px
from pathlib import Path

dash.register_page(__name__, path="/flights", name="Flights")

DATA = Path("data/clean/flights_2015_clean.csv")
DF = pd.read_csv(DATA) if DATA.exists() else None

def layout():
    if DF is None or DF.empty:
        return html.Div([
            html.H2("Flights — Dashboard"),
            html.Div(className="card", children=[
                html.P("⚠️ Données non trouvées. Placez le fichier :"),
                html.Code("data/clean/flights_2015_clean.csv")
            ])
        ])
    # Exemple minimal (à adapter)
    fig = px.scatter(DF.iloc[:200], x=DF.columns[0], y=DF.columns[1], title="Aperçu Flights (à adapter)")
    return html.Div([html.H2("Flights — Dashboard"), dcc.Graph(figure=fig)])
