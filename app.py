# app.py
from dash import Dash, html
import dash
import dash_bootstrap_components as dbc

# --- Application ---
app = Dash(
    __name__,
    use_pages=True,                       # active Dash Pages (dossier /pages)
    external_stylesheets=[dbc.themes.DARKLY],

    title="Dazzle Dash",
    suppress_callback_exceptions=True     # pratique si certaines callbacks sont sur d'autres pages
)
server = app.server

# --- Navbar (Bootstrap) ---
navbar = dbc.NavbarSimple(
    brand="Dazzle Dash",
    brand_href="/",                       # clic sur le brand -> Accueil (/)
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Accueil", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("Life (WHO)", href="/life", active="exact")),
        dbc.NavItem(dbc.NavLink("Food", href="/food", active="exact")),
        dbc.NavItem(dbc.NavLink("Flights", href="/flights", active="exact")),
    ],
)

# --- Layout principal ---
app.layout = dbc.Container(
    [
        navbar,
        html.Div(dash.page_container, className="pt-3")  # contenu des pages
    ],
    fluid=True
)

# --- Lancement ---
if __name__ == "__main__":
    app.run(debug=True)
