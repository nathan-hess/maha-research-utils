"""Configuration panel tab for uploading and managing simulation results
data files.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import (
    TAB_BAR_PADDING,
)
from .utils_generate_table import empty_file_table


def data_files_tab():
    """Creates the configuration panel tab where simulation results files can
    be uploaded and managed"""
    return [
        dash.html.H5('Data Upload', style={'marginTop': TAB_BAR_PADDING}),
        dash.html.P('Upload a new simulation results file here.'),
        dbc.Spinner(
            dash.dcc.Upload(
                'Drag and Drop or Click to Browse',
                id='upload-data',
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'marginLeft': '0px',
                    'marginRight': '0px',
                },
            ),
            # Delay prevents showing spinner when using switches or delete button
            delay_show=200,
        ),
        _file_name_input_box(),
        dash.html.Hr(),
        dash.html.H5('Current Files'),
        dash.html.P('Manage your uploaded simulation results files here.'),
        empty_file_table(),
    ]


def _file_name_input_box():
    return dbc.Spinner(
        dash.html.Div(
            dbc.Stack([
                # File name input box
                dbc.Row([
                    dbc.Col(
                        dbc.Input(
                            placeholder='Enter a name for your file...',
                            id='user-file-name',
                        ),
                        width=9, style={'marginTop': '10px'},
                    ),
                    dbc.Col(
                        dbc.Button('Load', id='load-file-button', disabled=False),
                        width=3, style={'marginTop': '10px'},
                    ),
                ]),

                # Overwrite warning alert
                dbc.Row(
                    dbc.Alert(
                        [
                            dash.html.H5([
                                dash.html.I(className='fa fa-exclamation-triangle'),
                                ' WARNING',
                            ]),
                            dash.html.Hr(),
                            dash.html.P(
                                'A file with this name already exists and '
                                'will be overwritten if you click "Load"'
                            ),
                        ],
                        id='file-overwrite-alert',
                        color='warning',
                        style={
                            'width': '95%',
                            'marginTop': '10px',
                            'marginLeft': '10px',
                            'marginRight': '10px',
                        },
                        is_open=False,
                        dismissable=True,
                    ),
                ),
            ]),
            id='div-user-file-name',
            hidden=True,
        ),
        # Delay prevents showing spinner when clearing "contents" (after
        # loading simulation results file)
        delay_show=500,
    )
