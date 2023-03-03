"""A web app-like graphical user interface for viewing Maha Multics simulation
results.
"""

# Some linter settings are disabled due to incompatibility with standard Dash
# coding practice
#
# pylint: disable=unused-argument

import argparse
import sys
from typing import List, Optional

# Mypy type checking is disabled for several packages because they are not
# PEP 561-compliant
import dash                              # type: ignore
from dash import Input, Output, State    # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from .constants import PROJECT_NAME, GUI_SHORT_NAME, VERSION
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
app.title = f'{PROJECT_NAME} {GUI_SHORT_NAME} v{VERSION}'


def main(argv: Optional[List[str]] = None) -> int:
    """Main entrypoint for running MahaUtils simulation results viewer"""
    # Command-line argument parsing
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog='MahaUtilsSimViewer',
        description=('The MahaUtils Simulation Results Viewer is a graphical '
                     'tool that aids in reading Maha Multics simulation '
                     'results files and viewing results. Project documentation '
                     'can be found at https://mahautils.readthedocs.io.'),
    )
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('--debug', action='store_true',
                        help=('enable Dash\'s debug mode (more information: '
                              'https://dash.plotly.com/devtools)'))
    args = parser.parse_args(argv)

    # Create and load Dash app
    app.layout = dash.html.Div([
        _app_header(),
        _graph(),
        _plot_controls(),
        _info_box(),
    ])

    app.run_server(debug=bool(args.debug))
    return 0


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
