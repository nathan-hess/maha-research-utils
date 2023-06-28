"""Code that generates the table of loaded simulation results files.
"""

from typing import Any, Dict

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import SIM_RESULTS_DICT_T


def empty_file_table():
    """Generates an empty table which can display a list of currently uploaded
    simulation results files"""
    return dbc.Table(
        [
            dash.html.Thead(dash.html.Tr(_table_header())),
            dash.html.Tbody(id='file-list-table-body'),
        ],
    )


def generate_file_table_body(sim_results_files: SIM_RESULTS_DICT_T,
                             metadata: Dict[str, Dict[str, Any]]):
    """Populates the simulation results file table with all currently uploaded
    simulation results files"""
    description_style = {
        'fontSize': 12.5,
        'marginTop': 0,
        'marginBottom': 0,
        'paddingTop': 0,
        'paddingBottom': 0,
    }

    description_header_style = description_style.copy()
    description_header_style['fontSize'] += 1.5

    contents = []
    for _, key in enumerate(sim_results_files.keys()):
        display_metadata = []

        title = sim_results_files[key].title
        sim_version = sim_results_files[key].sim_version
        if (title is not None) or (sim_version is not None):
            display_metadata.append(
                dash.html.B('Simulation Metadata',
                            style=description_header_style)
            )

            if title is not None:
                display_metadata.append(
                    dash.html.P(
                        [dash.html.B('Title: '), title],
                        style=description_style,
                    )
                )

            if sim_version is not None:
                display_metadata.append(
                    dash.html.P(
                        [dash.html.B('Version: '), sim_version],
                        style=description_style,
                    )
                )

        maha_multics_version = sim_results_files[key].maha_multics_version
        maha_multics_commit = sim_results_files[key].maha_multics_commit
        if (maha_multics_version is not None) or (maha_multics_commit is not None):
            if (title is not None) or (sim_version is not None):
                display_metadata.append(dash.html.P())

            display_metadata.append(
                dash.html.B('Maha Multics Metadata',
                            style=description_header_style)
            )

            if maha_multics_version is not None:
                display_metadata.append(
                    dash.html.P(
                        [dash.html.B('Version: '),
                         maha_multics_version],
                        style=description_style,
                    )
                )

            if maha_multics_commit is not None:
                display_metadata.append(
                    dash.html.P(
                        [dash.html.B('Commit: '),
                         maha_multics_commit],
                        style=description_style,
                    )
                )

        if len(display_metadata) == 0:
            file_id_description = dash.html.H6(key)
        else:
            file_id_description = dash.html.Details(
                [dash.html.Summary(key, style={'marginBottom': 5})]
                + display_metadata
            )

        contents.append(dash.html.Tr([
            dash.html.Td(dbc.Switch(
                value=metadata[key]['enabled'],
                id={'component': 'file-table-switch', 'key': key},
            )),
            dash.html.Td(file_id_description),
            dash.html.Td(dbc.Button(
                dash.html.I(className='bi bi-trash'),
                color='danger',
                id={'component': 'file-table-delete-button', 'key': key},
            )),
        ]))

    return contents


def _table_header():
    return [
        dash.html.Th('Enabled', style={'width': '15%'}),
        dash.html.Th('Name', style={'width': '70%'}),
        dash.html.Th('Delete', style={'width': '15%'}),
    ]
