"""Page elements for uploading simulation results files."""

from typing import Dict, Union

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.simresults import SimResults
from mahautils.multics.exceptions import SimResultsDataNotFoundError


def is_exportable(key: str, sim_results: SimResults):
    """Returns whether a simulation results variable has data associated with it
    in the simulation results file"""
    if sim_results.num_time_steps == 0:
        return True

    try:
        data = sim_results.get_data(key, sim_results.get_units(key))
    except SimResultsDataNotFoundError:
        return False

    return len(data) == sim_results.num_time_steps


def parse_sim_results_vars(sim_results: SimResults
                           ) -> Dict[str, Dict[str, Union[bool, str]]]:
    """Returns a dictionary containing all simulation results variables and
    their units from a Maha Multics simulation results file"""
    data: Dict[str, Dict[str, Union[bool, str]]] = {}

    for key in sim_results.variables:
        if is_exportable(key, sim_results):
            data[key] = {
                'export': True,
                'description': str(sim_results.get_description(key)),
                'units': sim_results.get_units(key),
            }

    return data


def upload_section():
    """Page elements to upload simulation results file"""
    return dash.html.Div([
        dash.html.H3('Step 1: Upload Simulation Results File'),
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
        dash.html.Div(
            dash.html.P(
                'Error: Unable to load simulation results file',
                id='upload-error-message',
                style={'color': 'red'},
            ),
            hidden=True,
            id='upload-error',
            style={'marginTop': '10px'},
        ),
        dbc.Toast(
            'Your data file was successfully uploaded.',
            header='Success!',
            id='upload-notification',
            dismissable=True,
            duration=5000,
            icon='success',
            is_open=False,
            style={
                'position': 'fixed',
                'bottom': 10,
                'right': 10,
            },
        ),
    ])
