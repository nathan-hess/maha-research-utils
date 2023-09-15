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
from typing import Dict, List, Optional, Union
import webbrowser

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
from dash import Input, Output, State    # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics import SimResults

from .constants import GUI_SHORT_NAME, PROJECT_NAME, VERSION
from .export import export_area, export_config_table
from .header import app_header
from .io_utils import load_simresults, sim_results_to_csv
from .store import export_config_store
from .upload import parse_sim_results_vars, upload_section


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
            export_config_store(),
            app_header(),
            upload_section(),
            export_area(),
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
_simresults = SimResults()


## APP CALLBACKS -------------------------------------------------------------
@app.callback(
    Output('upload-error', 'hidden'),
    Output('upload-error-message', 'children'),
    Output('export-section', 'hidden'),
    Output('export-config-store', 'data'),
    Output('export-options-section', 'children'),
    Input('upload-data', 'contents'),
    State('export-config-store', 'data'),
    prevent_initial_call=True,
)
def load_file(contents: Optional[str],
              config: Optional[Dict[str, Dict[str, Union[bool, str]]]]):
    """Uploads a simulation results file
    """
    # If file has not yet been uploaded, only show upload section
    if contents is None:
        return True, '', True, None, None

    # If user just uploaded a simulation results file, parse it and initialize
    # store with all simulation results variables
    if dash.ctx.triggered_id == 'upload-data':
        try:
            load_simresults(contents, _simresults)
        except Exception as exception:
            return (
                False,
                f'Error: Unable to read simulation results file ({exception})',
                True, None, None)

        new_config = parse_sim_results_vars(_simresults)

    return (
        True, '', False, new_config,
        export_config_table(_simresults, new_config))


@app.callback(
    Output('csv-download', 'data'),
    Input('export-button', 'n_clicks'),
    State('export-config-store', 'data'),
    prevent_initial_call=True,
)
def export_csv(n_clicks: Optional[int],
               config: Optional[Dict[str, Dict[str, Union[bool, str]]]]):
    """Saves the simulation results data to a CSV file and makes it
    available to the user as a download"""
    if config is None:
        raise dash.exceptions.PreventUpdate

    data = {
        'base64': False,
        'content': sim_results_to_csv(_simresults, config),
        'filename': 'simulation_results_data.csv',
    }
    return data
