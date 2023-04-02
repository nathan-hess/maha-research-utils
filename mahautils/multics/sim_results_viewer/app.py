"""A web app-like graphical user interface for viewing Maha Multics simulation
results.
"""

# Some linter settings are disabled due to incompatibility with standard Dash
# coding practice or to improve the app's user experience
#
# pylint: disable=unused-argument,broad-exception-caught

import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import webbrowser

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
from dash import Input, Output, State    # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import plotly.graph_objects as go        # type: ignore

from mahautils.utils import Dictionary
from .constants import (
    PROJECT_NAME,
    GUI_SHORT_NAME,
    SIM_RESULTS_DICT_T,
    VERSION,
)
from .error_box import error_box, generate_error_box_text
from .header import app_header
from .info import info_box
from .load_files import (
    load_plot_config,
    load_plot_config_error_message,
    load_simresults,
    plot_config_to_str,
)
from .panel import (
    generate_file_table_body,
    render_general_settings,
    render_x_settings,
    simviewer_config_panel,
)
from .plotting import graph, update_graph
from .store import (
    file_metadata_store,
    plot_config_general_store,
    plot_config_x_store,
    plot_config_y_store,
)


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
        prog='SimViewer',
        description=('The MahaUtils Simulation Results Viewer is a graphical '
                     'tool that aids in reading Maha Multics simulation '
                     'results files and viewing results. Project documentation '
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
    app.layout = dash.html.Div([
        file_metadata_store(),
        plot_config_general_store(),
        plot_config_x_store(),
        plot_config_y_store(),
        app_header(),
        graph(),
        simviewer_config_panel(),
        info_box(),
        error_box({'component': 'error-box', 'id': 'load-simresults'}),
        error_box({'component': 'error-box', 'id': 'update-config'}),
        error_box({'component': 'error-box', 'id': 'update-plot'}),
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
    Output('data-file-store', 'data'),
    Output('upload-data', 'contents'),
    Output({'component': 'error-box', 'id': 'load-simresults'}, 'is_open'),
    Output({'component': 'error-box-text', 'id': 'load-simresults-text'},
           'children'),
    Input('load-file-button', 'n_clicks'),
    Input({'component': 'file-table-switch', 'key': dash.ALL}, 'value'),
    Input({'component': 'file-table-delete-button', 'key': dash.ALL}, 'n_clicks'),
    State({'component': 'file-table-switch', 'key': dash.ALL}, 'id'),
    State('user-file-name', 'value'),
    State('file-list-table-body', 'children'),
    State('data-file-store', 'data'),
    State('upload-data', 'contents'),
)
def data_file_manager(
    ## Inputs ##
    n_clicks: int,
    enabled_switch_values: Optional[List[bool]],
    delete_button_clicks: Optional[List[int]],
    ## States ##
    enabled_switch_ids: Optional[List[Dict[str, Any]]],
    name: Optional[str],
    current_file_table: Optional[list],
    metadata: Optional[Dict[str, Dict[str, Any]]],
    contents: Optional[str],
):
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
    updated_contents = None
    if dash.ctx.triggered_id is None:
        # Callback was triggered by initial page load, so skip
        # other actions and render table
        pass

    elif dash.ctx.triggered_id == 'load-file-button':
        if (contents is not None) and (name is not None):
            try:
                _sim_results_files[name] = load_simresults(contents)
            except Exception as exception:
                error_box_text = generate_error_box_text(
                    dash.html.P(
                        f'Unable to read simulation results file "{name}."'),
                    exception,
                )
                return (current_file_table, metadata, contents,
                        True, error_box_text)
            metadata[name] = {'enabled': True}

    elif dash.ctx.triggered_id['component'] == 'file-table-switch':
        for i, value in enumerate(enabled_switch_values):  # type: ignore
            key = enabled_switch_ids[i]['key']  # type: ignore
            metadata[key]['enabled'] = value

        updated_contents = contents

    elif dash.ctx.triggered_id['component'] == 'file-table-delete-button':
        key = dash.ctx.triggered_id['key']
        del _sim_results_files[key]
        del metadata[key]

        updated_contents = contents

    return (
        generate_file_table_body(_sim_results_files, metadata),
        metadata,
        updated_contents,
        False,
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
        if filename.endswith('.txt'):
            filename = filename[:-4]

        return False, filename

    return True, 'NONE'


@app.callback(
    Output('file-overwrite-alert', 'is_open'),
    Output('load-file-button', 'disabled'),
    Output('upload-data', 'filename'),
    Input('user-file-name', 'value'),
    prevent_initial_call=True,
)
def validate_upload_file_name(name: Optional[str]):
    """Checks that the user provided a valid file description for a simulation
    results file"""
    overwrite_alert_open = False
    load_button_disabled = False

    if (name is None) or (name in _sim_results_files):
        overwrite_alert_open = True
        load_button_disabled = False
    elif len(name) <= 0:
        overwrite_alert_open = False
        load_button_disabled = True

    return overwrite_alert_open, load_button_disabled, name


## PLOT CONFIGURATION --------------------------------------------------------
@app.callback(
    Output('plot-config-upload', 'contents'),
    Output('plot-config-general-store', 'data'),
    Output('plot-config-x-store', 'data'),
    Output('plot-config-y-store', 'data'),
    Output({'component': 'error-box', 'id': 'update-config'}, 'is_open'),
    Output({'component': 'error-box-text', 'id': 'update-config-text'}, 'children'),
    Input('plot-config-upload', 'contents'),
    Input('data-file-store', 'data'),
    Input({'component': 'plot-config', 'tab': 'general', 'field': 'title'}, 'value'),              # noqa: E501  # pylint: disable=C0301
    Input({'component': 'plot-config', 'tab': 'general', 'field': 'background-color'}, 'value'),   # noqa: E501  # pylint: disable=C0301
    Input({'component': 'plot-config', 'tab': 'general', 'field': 'grid-x'}, 'value'),             # noqa: E501  # pylint: disable=C0301
    Input({'component': 'plot-config', 'tab': 'general', 'field': 'grid-y'}, 'value'),             # noqa: E501  # pylint: disable=C0301
    Input({'component': 'plot-config', 'tab': 'general', 'field': 'append-units'}, 'value'),       # noqa: E501  # pylint: disable=C0301
    Input({'component': 'plot-config', 'tab': 'general', 'field': 'freeze-uirevision'}, 'value'),  # noqa: E501  # pylint: disable=C0301
    Input({'component': 'plot-config', 'tab': 'general', 'field': 'hovermode'}, 'value'),          # noqa: E501  # pylint: disable=C0301
    Input({'component': 'plot-config', 'tab': 'x', 'field': 'variable'}, 'value'),
    Input({'component': 'plot-config', 'tab': 'x', 'field': 'units'}, 'value'),
    Input({'component': 'plot-config', 'tab': 'x', 'field': 'title'}, 'value'),
    Input({'component': 'plot-config', 'tab': 'x', 'field': 'xmin'}, 'value'),
    Input({'component': 'plot-config', 'tab': 'x', 'field': 'xmax'}, 'value'),
    Input({'component': 'plot-config', 'tab': 'x', 'field': 'tick_spacing'}, 'value'),  # noqa: E501  # pylint: disable=C0301
    State('plot-config-general-store', 'data'),
    State('plot-config-x-store', 'data'),
    State('plot-config-y-store', 'data'),
    State({'component': 'error-box', 'id': dash.ALL}, 'is_open'),
    prevent_initial_call=True,
)
def update_plot_config(
    ## Inputs ##
    upload_contents: Optional[str],
    file_metadata: dict,
    plot_title: Optional[str],
    background_color: Optional[str],
    grid_x_enabled: Optional[bool],
    grid_y_enabled: Optional[bool],
    append_units: Optional[bool],
    freeze_uirevision: Optional[bool],
    hovermode: Optional[str],
    x_variable: Optional[str],
    x_units: Optional[str],
    x_title: Optional[str],
    x_min,
    x_max,
    x_tick_spacing,
    ## States ##
    config_general: dict,
    config_x: dict,
    config_y: dict,
    error_boxes_open: List[bool],
):
    """Updates the browser storage containing the plot configuration data"""
    if any(error_boxes_open):
        # If any error boxes are open, prevent updating the app so user can
        # resolve the issue first
        raise dash.exceptions.PreventUpdate

    if dash.ctx.triggered_id == 'plot-config-upload':
        if upload_contents is None:
            # Either callback was run in initial call, or it was already
            # triggered and automatically reset the upload "contents" to None.
            # In either case, no update is necessary
            raise dash.exceptions.PreventUpdate

        try:
            new_general, new_x, new_y = load_plot_config(upload_contents)
            update_graph(new_general, new_x, new_y, _sim_results_files)
        except Exception as exception:
            error_text = generate_error_box_text(load_plot_config_error_message,
                                                 exception)

            return None, config_general, config_x, config_y, True, error_text

        config_general = new_general
        config_x = new_x
        config_y = new_y

    else:
        # General plot configuration settings
        config_general['title'] = plot_title

        if background_color is not None:
            config_general['background_color'] = background_color

        if grid_x_enabled is not None:
            config_general['grid_x'] = grid_x_enabled

        if grid_y_enabled is not None:
            config_general['grid_y'] = grid_y_enabled

        if append_units is not None:
            config_general['append_units'] = append_units

        if hovermode is not None:
            config_general['hovermode'] = hovermode

        if freeze_uirevision is not None:
            config_general['freeze_uirevision'] = freeze_uirevision

        # Plot configuration settings for x-axis
        if x_variable is not None:
            if x_variable != config_x['variable']:
                x_units = ''

            config_x['variable'] = x_variable

        config_x['units'] = x_units

        config_x['axis_title'] = x_title

        config_x['xmin'] = None if x_min in (None, '') else float(x_min)
        config_x['xmax'] = None if x_max in (None, '') else float(x_max)
        config_x['tick_spacing'] = None if x_tick_spacing in (None, '') \
                                        else float(x_tick_spacing)  # noqa: E127

    return None, config_general, config_x, config_y, False, None


@app.callback(
    Output('config-export-download', 'data'),
    Input('config-export-button', 'n_clicks'),
    State('plot-config-general-store', 'data'),
    State('plot-config-x-store', 'data'),
    State('plot-config-y-store', 'data'),
    prevent_initial_call=True,
)
def export_plot_config(n_clicks: Optional[int], config_general: dict,
                       config_x: dict, config_y: dict):
    """Saves the current plot configuration options in a file and makes it
    available to the user as a download"""
    data = {
        'base64': False,
        'content': plot_config_to_str(config_general, config_x, config_y),
        'filename': 'mahautils_simviewer_config.json',
    }
    return data


@app.callback(
    Output('plot-config-general-settings', 'children'),
    Input('plot-config-general-store', 'data'),
)
def render_ui_general(config_general: dict):
    """Generates the UI elements that allow the user to configure general
    plot settings"""
    return render_general_settings(config_general)


@app.callback(
    Output('plot-config-x-settings', 'children'),
    Input('plot-config-x-store', 'data'),
)
def render_ui_x(config_x: dict):
    """Generates the UI elements that allow the user to configure x-axis
    plot settings"""
    return render_x_settings(config_x, _sim_results_files)


## PLOTTING ------------------------------------------------------------------
@app.callback(
    Output('plotly-graph', 'figure'),
    Output({'component': 'error-box', 'id': 'update-plot'}, 'is_open'),
    Output({'component': 'error-box-text', 'id': 'update-plot-text'}, 'children'),
    Input('plot-config-general-store', 'data'),
    Input('plot-config-x-store', 'data'),
    Input('plot-config-y-store', 'data'),
    Input('data-file-store', 'data'),
    State('plotly-graph', 'figure'),
    State({'component': 'error-box', 'id': dash.ALL}, 'is_open'),
    prevent_initial_call=True,
)
def update_plot(
    ## Inputs ##
    config_general: dict,
    config_x: dict,
    config_y: dict,
    file_metadata: dict,
    ## States ##
    current_figure: go.Figure,
    error_boxes_open: List[bool],
):
    """Updates the simulation results plot any time the plot configuration
    data dictionary changes"""
    if any(error_boxes_open):
        # If any error boxes are open, prevent updating the app so user can
        # resolve the issue first
        raise dash.exceptions.PreventUpdate

    if config_x['units'] in (None, ''):
        # If the user just changed the x-axis simulation results variable,
        # wait to update the plot to give them a chance to set the units
        raise dash.exceptions.PreventUpdate

    try:
        figure = update_graph(
            config_general    = config_general,
            config_x          = config_x,
            config_y          = config_y,
            sim_results_files = _sim_results_files,
        )

        error_box_is_open = False
        error_box_text = None

    except Exception as exception:
        figure = current_figure
        error_box_is_open = True
        error_box_text = generate_error_box_text(
            dash.html.P('Unable to update plot.  There is likely a mistake '
                        'in the plot configuration options you have selected.'),
            exception,
        )

    return figure, error_box_is_open, error_box_text


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
