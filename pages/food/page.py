from dash import html, dcc
import plotly.express as px
from utils.loaders import get_food
from . import ids

def layout():
    df = get_food()
    # Placeholder : on affichera un graph réel après nettoyage
    fig = px.scatter(title="Food — à compléter")
    return html.Div([
        html.H2("Food Production / Consumption"),
        dcc.Graph(id=ids.GRAPH_MAIN, figure=fig)
    ])
