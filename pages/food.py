from dash import html, dcc
import dash
import pandas as pd
import plotly.express as px
from pathlib import Path

dash.register_page(__name__, path="/food", name="Food")

DATA = Path("data/clean/food_clean.csv")
DF = pd.read_csv(DATA) if DATA.exists() else None

def layout():
    if DF is None or DF.empty:
        return html.Div([
            html.H2("Food — Dashboard"),
            html.Div(className="card", children=[
                html.P("⚠️ Données non trouvées. Placez le fichier :"),
                html.Code("data/clean/food_clean.csv")
            ])
        ])
    # Exemple minimal (à adapter aux colonnes)
    fig = px.scatter(DF.iloc[:200], x=DF.columns[0], y=DF.columns[1], title="Aperçu Food (à adapter)")
    return html.Div([html.H2("Food — Dashboard"), dcc.Graph(figure=fig)])
