"""Page elements for uploading simulation results files."""

from typing import Dict, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics import SimResults


def parse_sim_results_vars(sim_results: SimResults
                           ) -> Dict[str, Dict[str, Union[bool, str]]]:
    """Returns a dictionary containing all simulation results variables and
    their units from a Maha Multics simulation results file"""
    data: Dict[str, Dict[str, Union[bool, str]]] = {}

    for key in sim_results.variables:
        data[key] = {
            'export': True,
            'units': sim_results.get_units(key),
        }

    return data


def upload_section():
    """Page elements to upload simulation results file"""
    return dash.html.Div([
        dash.html.H3('Step 1: Upload Simulation Results File'),
        dbc.Spinner(
            dash.dcc.Upload(
                'Drag and Drop or Click to Browse',
                id='upload-data',
                style={
                    'width': '30%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'marginTop': '20px',
                    'marginLeft': '0px',
                    'marginRight': '0px',
                },
            ),
            delay_show=200,
        ),
        dash.html.Div(
            dash.html.P(
                'Error: Unable to load simulation results file',
                id='upload-error-message',
                style={'color': 'red'},
            ),
            hidden=True,
            id='upload-error',
            style={'marginTop': '10px'},
        )
    ])
