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

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
from dash import Input, Output, State    # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.utils import Dictionary
from .constants import (
    PROJECT_NAME,
    GUI_SHORT_NAME,
    SIM_RESULTS_FILE_T,
    VERSION,
)
from .header import app_header
from .info import info_box
from .panel import (
    generate_file_table_body,
    simviewer_config_panel,
)
from .plotting import graph
from .utils import load_simresults


app = dash.Dash(
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
    ],
    update_title=None,
)
app.title = f'{PROJECT_NAME} {GUI_SHORT_NAME}'


# Global variables for data storage
#
# In general, it is not a good idea to use global variables in Dash apps
# (https://dash.plotly.com/sharing-data-between-callbacks).  However, there
# are several reasons global variables are suitable for this use case:
#
# 1. This app is intended to be run locally, not on a shared server.
# 2. The app needs to be able to load arbitrarily large simulation results
#    files.  Some can be hundreds of megabytes, which will likely exceed
#    many browser quotas.
# 3. The `SimResults` object performs a number of file-parsing and analysis
#    tasks.  If serializing session data to JSON, it would be necessary to
#    perform these tasks on each load, which could be time-consuming for
#    large files and result in poor visual performance.
# 4. Users may want to open the same simulation results files in multiple
#    tabs/windows.  By using a global variable, the same files will be
#    displayed in all browser tabs/windows.

_sim_results_files: SIM_RESULTS_FILE_T = Dictionary()


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
    parser.add_argument('--port', action='store', type=int, default=8050,
                        help='port on which to serve the app (default is 8050)')
    args = parser.parse_args(argv)

    # Create and load Dash app
    app.layout = dash.html.Div([
        app_header(),
        graph(),
        simviewer_config_panel(),
        info_box(),
    ])

    app.run_server(debug=bool(args.debug), port=int(args.port))

    return 0


@app.callback(
    Output('file-list-table-body', 'children'),
    Output('upload-data', 'contents'),
    Input('load-file-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('user-file-name', 'value'),
)
def generate_file_table(n_clicks: int, contents: Optional[str], name: Optional[str]):
    """Reads uploaded simulation results from a file"""
    if (contents is not None) and (name is not None):
        _sim_results_files[name] = {'file': load_simresults(contents), 'enabled': True}

    return generate_file_table_body(_sim_results_files), None


@app.callback(
    Output('div-user-file-name', 'hidden'),
    Output('user-file-name', 'value'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
)
def hide_show_upload_filename(contents: Optional[str], filename: Optional[str]):
    """Hides/shows the file naming box and populates the input area with
    a default name based on the uploaded file"""
    if (contents is not None) and (filename is not None):
        return False, filename.strip('.txt')

    return True, 'NONE'


@app.callback(
    Output('upload-data', 'disabled'),
    Input({'component': 'file-table-switch', 'index': dash.ALL}, 'value'),
    State({'component': 'file-table-switch', 'index': dash.ALL}, 'id'),
    State('upload-data', 'disabled'),
    prevent_initial_call=True,
)
def store_file_table_enabled(values, ids, x):
    """Stores whether each simulation results file is enabled or disabled in
    the plot control panel"""
    for i, value in enumerate(values):
        key = list(_sim_results_files.keys())[ids[i]['index']]
        _sim_results_files[key]['enabled'] = bool(value)

    return x


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


@app.callback(
    Output('file-overwrite-alert', 'is_open'),
    Input('user-file-name', 'value'),
    prevent_initial_call=True,
)
def validate_upload_file_name(name: Optional[str]):
    """Checks that the user provided a valid file description for a simulation
    results file"""
    if (name is None) or (len(name) <= 0) or (name in _sim_results_files):
        return True

    return False
