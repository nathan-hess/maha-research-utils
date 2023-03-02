"""A web app-like graphical user interface for viewing Maha Multics simulation
results.
"""

import dash
from dash import Input, Output, State
import dash_bootstrap_components as dbc

from .header import _app_header
from .info import _info_box
from .plotting import _graph, _plot_controls

app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
    ]
)
app.title = 'MahaUtils SimViewer'


def main() -> None:
    """Main entrypoint for running MahaUtils simulation results viewer"""
    app.layout = dash.html.Div([
        _app_header(),
        _graph(),
        _plot_controls(),
        _info_box(),
    ])

    app.run_server(debug=True)


@app.callback(
    Output('info-button-modal', 'is_open'),
    Input('info-button', 'n_clicks'),
    Input('info-box-close-button', 'n_clicks'),
    State('info-button-modal', 'is_open'),
    prevent_initial_call=True,
)
def toggle_info_box(n_clicks_open, n_clicks_close, is_open):
    """Callback which opens and closes the modal information box
    """
    return not is_open


@app.callback(
    Output('plot-config-panel', 'is_open'),
    Input('plot-config-button', 'n_clicks'),
    State('plot-config-panel', 'is_open'),
    prevent_initial_call=True,
)
def toggle_plot_config_panel(n_clicks, is_open):
    """Callback which opens and closes the plot configuration panel
    """
    return not is_open
