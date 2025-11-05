# callbacks.py
from dash import Input, Output, html

def register_callbacks(app):
    @app.callback(Output("page-content", "children"),
                  Input("url", "pathname"))
    def render_page(pathname):
        try:
            # imports paresseux (évite crash au démarrage)
            if pathname == "/food":
                from pages.food.page import layout as food_layout
                return food_layout()
            if pathname == "/flights":
                from pages.flights.page import layout as flights_layout
                return flights_layout()
            # défaut : WHO
            from pages.who_life.page import layout as life_layout
            return life_layout()
        except Exception as e:
            # Affiche l'erreur dans l'UI pour qu'on la voie
            return html.Div(
                style={"background":"#fff3f3","border":"1px solid #ffcccc",
                       "padding":"16px","borderRadius":"12px"},
                children=[
                    html.H3("Erreur lors du rendu de la page", style={"color":"#c00","marginTop":"0"}),
                    html.P("Vérifie les points suivants :"),
                    html.Ul([
                        html.Li("Les fichiers __init__.py existent dans utils/ et pages/*"),
                        html.Li("Le fichier WHO brut est bien : data/raw/Life Expectancy Data.csv"),
                        html.Li("pages/who_life/page.py n'accède pas à des colonnes absentes"),
                    ]),
                    html.P("Détail technique :"),
                    html.Pre(str(e), style={"whiteSpace":"pre-wrap","fontSize":"12px"})
                ]
            )
