# pages/home.py
from dash import html
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Accueil")

def layout():
    return dbc.Container(
        [
            # Hero / en-tête
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Bienvenue sur Dazzle Dash 🌍", className="display-5 fw-bold"),
                        html.P(
                            "Explorez des visualisations interactives : espérance de vie (WHO), "
                            "alimentation et voyages.",
                            className="lead text-muted"
                        ),
                    ],
                    width=12, className="py-4",
                )
            ),

            # Cartes de navigation
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("💖 Life (WHO)", className="card-title"),
                                        html.P(
                                            "Espérance de vie, HDI (annuel), scolarité, mortalité adulte.",
                                            className="card-text"
                                        ),
                                        dbc.Button("Ouvrir", href="/life", color="primary"),
                                    ]
                                )
                            ],
                            className="shadow-sm h-100",
                        ),
                        md=4, className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("🍔 Food", className="card-title"),
                                        html.P(
                                            "Indicateurs alimentaires et nutritionnels (exemples).",
                                            className="card-text"
                                        ),
                                        dbc.Button("Ouvrir", href="/food", color="primary"),
                                    ]
                                )
                            ],
                            className="shadow-sm h-100",
                        ),
                        md=4, className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4("✈️ Flights", className="card-title"),
                                        html.P(
                                            "Tendances des vols, destinations et métriques de voyage.",
                                            className="card-text"
                                        ),
                                        dbc.Button("Ouvrir", href="/flights", color="primary"),
                                    ]
                                )
                            ],
                            className="shadow-sm h-100",
                        ),
                        md=4, className="mb-4",
                    ),
                ],
                className="py-2",
            ),

            # Section “à propos” (optionnelle)
            dbc.Row(
                dbc.Col(
                    dbc.Alert(
                        [
                            html.Strong("Astuce : "),
                            "utilise le menu en haut ou les cartes pour naviguer. "
                            "Tu peux changer les textes/images quand tu veux."
                        ],
                        color="info", className="mt-2",
                    ),
                    md=12,
                )
            ),

            # Footer simple
            html.Hr(),
            dbc.Row(
                dbc.Col(
                    html.Div("© Dazzle Dash — demo Dash Pages + Bootstrap", className="text-muted small py-2"),
                    width=12
                )
            ),
        ],
        fluid=True,
        className="py-3",
    )
