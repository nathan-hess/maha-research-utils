"""A web app-like graphical user interface for viewing Maha Multics simulation
results.
"""

# Some linter settings are disabled due to incompatibility with standard Dash
# coding practice
#
# pylint: disable=unused-argument

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import webbrowser

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
from dash import Input, Output, State    # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.utils import Dictionary
from .constants import (
    PROJECT_NAME,
    GUI_SHORT_NAME,
    SIM_RESULTS_DICT_T,
    VERSION,
)
from .header import app_header
from .info import info_box
from .panel import (
    generate_file_table_body,
    simviewer_config_panel,
)
from .plotting import graph
from .store import file_metadata_store
from .utils import load_simresults


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
    parser.add_argument('--no-browser', action='store_true',
                        help=('prevent automatically opening a browser window '
                              f'when launching {GUI_SHORT_NAME}'))
    args = parser.parse_args(argv)

    port = int(args.port)

    # Create and load Dash app
    app.layout = dash.html.Div([
        file_metadata_store(),
        app_header(),
        graph(),
        simviewer_config_panel(),
        info_box(),
    ])

    # Launch browser to display app
    if not bool(args.no_browser) and ('WERKZEUG_RUN_MAIN' not in os.environ):
        # Checking for the "WERKZEUG_RUN_MAIN" variable prevents opening a new
        # browser window each time source code changes are saved in debug mode
        webbrowser.open(f'http://127.0.0.1:{port}/')

    # Run web app
    app.run_server(debug=bool(args.debug), port=port)

    return 0


## GLOBAL VARIABLES FOR DATA STORAGE -----------------------------------------
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

_sim_results_files: SIM_RESULTS_DICT_T = Dictionary()


## DATA FILE MANAGEMENT ------------------------------------------------------
@app.callback(
    Output('file-list-table-body', 'children'),
    Output('data_file_store', 'data'),
    Output('upload-data', 'contents'),
    Input('load-file-button', 'n_clicks'),
    Input({'component': 'file-table-switch', 'key': dash.ALL}, 'value'),
    Input({'component': 'file-table-delete-button', 'key': dash.ALL}, 'n_clicks'),
    State({'component': 'file-table-switch', 'key': dash.ALL}, 'id'),
    State('upload-data', 'contents'),
    State('user-file-name', 'value'),
    State('data_file_store', 'data'),
)
def data_file_manager(
        ## Inputs ##
        n_clicks: int,
        enabled_switch_values: Optional[List[bool]],
        delete_button_clicks: Optional[List[int]],
        ## States ##
        enabled_switch_ids: Optional[List[Dict[str, Any]]],
        contents: Optional[str],
        name: Optional[str],
        metadata: Optional[Dict[str, Dict[str, Any]]]):
    """Reads uploaded simulation results from a file"""
    # Ensure that keys in file metadata store match current list of simulation
    # results files.  This is important if, for instance, multiple tabs are
    # opened, as each will have its own session storage.  This step ensures all
    # stores are synced with the global file list
    if metadata is None:
        metadata = {}

    metadata = {
        key: metadata.get(key, {'enabled':  True})
        for key in _sim_results_files.keys()
    }

    # Upload simulation results file or modify stored metadata
    if dash.ctx.triggered_id is None:
        # Callback was triggered by initial page load, so skip
        # other actions and render table
        pass

    elif dash.ctx.triggered_id == 'load-file-button':
        if (contents is not None) and (name is not None):
            _sim_results_files[name] = load_simresults(contents)
            metadata[name] = {'enabled': True}

    elif dash.ctx.triggered_id['component'] == 'file-table-switch':
        for i, value in enumerate(enabled_switch_values):  # type: ignore
            key = enabled_switch_ids[i]['key']  # type: ignore
            metadata[key]['enabled'] = value

    elif dash.ctx.triggered_id['component'] == 'file-table-delete-button':
        key = dash.ctx.triggered_id['key']
        del _sim_results_files[key]
        del metadata[key]

    return (
        generate_file_table_body(_sim_results_files, metadata),
        metadata,
        None,
    )


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


## HIDE/SHOW CONTROLS FOR CONFIGURATION PANES --------------------------------
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
