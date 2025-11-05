from dash import html, dcc
import dash_bootstrap_components as dbc

def navbar():
    return dbc.NavbarSimple(
        brand="Dazzle Dash",
        color="dark", dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Life (WHO)", href="/life")),
            dbc.NavItem(dbc.NavLink("Food", href="/food")),
            dbc.NavItem(dbc.NavLink("Flights", href="/flights")),
        ],
    )

layout = dbc.Container(
    [dcc.Location(id="url"),
     navbar(),
     html.Div(id="page-content", className="p-3")],
    fluid=True
)
