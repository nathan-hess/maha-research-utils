"""Code that generates the table of loaded simulation results files.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import SIM_RESULTS_FILE_T


def empty_file_table():
    """Generates an empty table which can display a list of currently uploaded
    simulation results files"""
    contents = dbc.Table(
        [
            dash.html.Thead(dash.html.Tr(_table_header())),
            dash.html.Tbody(id='file-list-table-body'),
        ],
    )

    return contents


def generate_file_table_body(sim_results_files: SIM_RESULTS_FILE_T):
    """Populates the simulation results file table with all currently uploaded
    simulation results files"""
    contents = []
    for i, key in enumerate(sim_results_files.keys()):
        contents.append(dash.html.Tr([
            dash.html.Td(dbc.Switch(
                value=False,
                id={'component': 'file-table-switch', 'index': i},
            )),
            dash.html.Td(dash.html.H6(key)),
            dash.html.Td(dbc.Button(
                dash.html.I(className='bi bi-trash'),
                color='danger',
                id={'component': 'file-table-delete-button', 'index': i},
            )),
        ]))

    return contents


def _table_header():
    return [
        dash.html.Th('Enabled', style={'width': '15%'}),
        dash.html.Th('Name', style={'width': '70%'}),
        dash.html.Th('Delete', style={'width': '15%'}),
    ]
