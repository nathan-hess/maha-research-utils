"""A web app-like graphical user interface for viewing Maha Multics simulation
results.
"""

import dash
import dash_bootstrap_components as dbc

from .header import _app_header

app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
    ]
)
app.title = 'Simulation Results Viewer'


def main() -> None:
    """Main entrypoint for running MahaUtils simulation results viewer"""
    app.layout = dash.html.Div([
        _app_header(),
    ])

    app.run_server(debug=True)
