"""A web app-like graphical user interface for exporting Maha Multics simulation
to a CSV file.
"""

# Some linter settings are disabled due to incompatibility with standard Dash
# coding practice or to improve the app's user experience
#
# pylint: disable=unused-argument,broad-exception-caught

import argparse
import os
import sys
from typing import List, Optional
import webbrowser

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
from dash import Input, Output, State    # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import plotly.graph_objects as go        # type: ignore

from mahautils.utils import Dictionary

from .constants import GUI_SHORT_NAME, PROJECT_NAME, VERSION
from .header import app_header
from .io_utils import load_simresults
from .upload import upload_section


## MAIN APP CONFIGURATION ----------------------------------------------------
app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
    ],
    update_title=None,
)
app.title = f'{PROJECT_NAME} {GUI_SHORT_NAME}'


def main(argv: Optional[List[str]] = None) -> int:
    """Main entrypoint for running MahaUtils simulation results viewer"""
    # Command-line argument parsing
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog=GUI_SHORT_NAME,
        description=('The MahaUtils Simulation Results Exporter is a graphical '
                     'tool that aids in saving Maha Multics simulation '
                     'results to a CSV file. Project documentation '
                     'can be found at https://mahautils.readthedocs.io.'),
    )
    parser.add_argument('--port', action='store', type=int, default=8050,
                        help='port on which to serve the app (default is 8050)')
    parser.add_argument('--debug', action='store_true',
                        help=('enable Dash\'s debug mode (more information: '
                              'https://dash.plotly.com/devtools)'))
    parser.add_argument('--no-browser', action='store_true',
                        help=('prevent automatically opening a browser window '
                              f'when launching {GUI_SHORT_NAME}'))
    parser.add_argument('--version', action='version', version=VERSION)

    args = parser.parse_args(argv)

    port = int(args.port)

    # Create and load Dash app
    app.layout = dash.html.Div(
        [
            app_header(),
            upload_section(),
        ],
        style={
            'marginLeft': '30px',
            'marginRight': '30px',
        }
    )

    # Launch browser to display app
    if not bool(args.no_browser) and ('WERKZEUG_RUN_MAIN' not in os.environ):
        # Checking for the "WERKZEUG_RUN_MAIN" variable prevents opening a new
        # browser window each time source code changes are saved in debug mode
        webbrowser.open(f'http://127.0.0.1:{port}/')

    # Run web app
    app.run_server(debug=bool(args.debug), port=port)

    return 0


## GLOBAL VARIABLES FOR DATA STORAGE -----------------------------------------
_simresults = None


## DATA FILE MANAGEMENT ------------------------------------------------------
@app.callback(
    Output('upload-error', 'hidden'),
    Output('upload-error-message', 'children'),
    Input('upload-data', 'contents'),
)
def load_file(contents: Optional[str]):
    """Uploads a simulation results file"""
    
    if contents is None:
        return True, ''

    try:
        _simresults = load_simresults(contents)
    except Exception as exception:
        return (
            False,
            f'Error: Unable to read simulation results file ({exception})'
        )

    return True, ''
