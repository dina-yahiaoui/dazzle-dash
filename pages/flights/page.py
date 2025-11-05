from dash import html, dcc
import plotly.express as px
from utils.loaders import get_flights
from . import ids

def layout():
    df = get_flights()
    # Placeholder : on affichera un graph réel après nettoyage
    fig = px.scatter(title="Flights — à compléter")
    return html.Div([
        html.H2("Flight Delays 2015"),
        dcc.Graph(id=ids.GRAPH_MAIN, figure=fig)
    ])
