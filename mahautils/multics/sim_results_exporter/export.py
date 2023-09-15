"""Page elements for saving simulation results data to a CSV file."""

from typing import Dict, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics import SimResults
from .io_utils import is_exportable


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
            dash.html.H5(
                'Customize Export',
                style={'marginTop': '20px'},
            ),
            dbc.Button('Select All', id='select-button',
                       style={'marginRight': '20px'}),
            dbc.Button('Deselect All', id='deselect-button'),
            dash.dcc.Loading(
                dash.html.Div(id='export-options-section'),
                fullscreen=False,
                style={'position': 'absolute', 'top': '0px'},
            ),
        ],
        hidden=True,
        id='export-section',
        style={
            'marginTop': '50px',
        },
    )


def export_config_table(sim_results: SimResults,
                        config: Dict[str, Dict[str, Union[bool, str]]]):
    """Generates a table to allow users to select which simulation results
    variables to export"""
    rows = []

    for key in sim_results.variables:
        if not is_exportable(key, sim_results):
            continue

        rows.append(
            dash.html.Tr([
                dash.html.Td(dbc.Checkbox(
                    value=config[key]['export'],
                    id={'component': 'config-export', 'key': key},
                )),
                dash.html.Td(key),
                dash.html.Td(sim_results.get_description(key)),
                dash.html.Td(dbc.Input(
                    value=sim_results.get_units(key),
                    id={'component': 'config-export', 'key': key},
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
