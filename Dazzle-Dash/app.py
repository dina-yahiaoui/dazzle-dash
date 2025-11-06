from dash import Dash, html
import dash
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           title="Dazzle Dash")
server = app.server

navbar = dbc.NavbarSimple(
    brand="Dazzle Dash",
    color="dark", dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Life (WHO)", href="/life")),
        dbc.NavItem(dbc.NavLink("Food", href="/food")),
        dbc.NavItem(dbc.NavLink("Flights", href="/flights")),
    ],
)

app.layout = dbc.Container([navbar, dash.page_container], fluid=True)

if __name__ == "__main__":
    app.run(debug=True)
