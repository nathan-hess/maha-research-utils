"""Page elements for saving simulation results data to a CSV file."""

from typing import Dict, Optional, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.simresults import SimResults
from .upload import parse_sim_results_vars


def export_area():
    """Page elements to save simulation results data to a CSV file"""
    return dash.html.Div(
        [
            dash.html.H3('Step 2: Export CSV File',
                         style={'marginBottom': '10px'}),
            dash.html.P(
                'Click the button below to save your simulation results '
                'data to a CSV file'
            ),
            dbc.Button('Export CSV', id='export-button'),
            dash.dcc.Download(id='csv-download'),
            dash.html.Div(
                [
                    dbc.Switch(
                        label='Customize Export',
                        id='custom-export-switch',
                        value=False,
                    ),
                    dash.html.I(
                        'Warning: Enabling this option can cause severe '
                        'performance issues, such as the page freezing, '
                        'for large simulation results files.  If your '
                        'file is large, it is recommended that you click '
                        '"Export CSV" above and then edit the data with '
                        'an application such as Microsoft Excel.'
                    ),
                ],
                style={'marginTop': '30px'},
            ),
            dash.html.Div(
                [
                    dash.html.H4('Customize Export', style={'marginTop': '30px'}),
                    dbc.Button('Select All', id='select-button',
                               style={'marginRight': '20px'}),
                    dbc.Button('Deselect All', id='deselect-button'),
                    dash.dcc.Loading(
                        dash.html.Div(id='export-options-section'),
                        fullscreen=False,
                        style={'position': 'absolute', 'top': '0px'},
                    ),
                ],
                id='custom-export-div',
            ),
        ],
        hidden=True,
        id='export-section',
        style={
            'marginTop': '50px',
        },
    )


def export_config_table(sim_results: SimResults,
                        config: Optional[Dict[str, Dict[str, Union[bool, str]]]]):
    """Generates a table to allow users to select which simulation results
    variables to export"""
    if config is None:
        config = parse_sim_results_vars(sim_results)

    rows = []
    for key in config:
        rows.append(
            dash.html.Tr([
                dash.html.Td(dbc.Checkbox(
                    value=config[key]['export'],
                    id={'component': 'config-export', 'key': key},
                )),
                dash.html.Td(key),
                dash.html.Td(config[key]['description']),
                dash.html.Td(dbc.Input(
                    value=config[key]['units'],
                    id={'component': 'config-units', 'key': key},
                    debounce=True,
                )),
            ])
        )

    return dbc.Table([
        dash.html.Thead(dash.html.Tr([
            dash.html.Th('Include', style={'width': '15%'}),
            dash.html.Th('Key', style={'width': '15%'}),
            dash.html.Th('Description', style={'width': '50%'}),
            dash.html.Th('Units', style={'width': '20%'}),
        ])),
        dash.html.Tbody(rows),
    ])


def update_select_boxes(config: Optional[Dict[str, Dict[str, Union[bool, str]]]],
                        setting: bool):
    """Sets all 'include in export' boxes to a user-specified setting"""
    if config is None:
        raise dash.exceptions.PreventUpdate

    for key in config:
        config[key]['export'] = setting
