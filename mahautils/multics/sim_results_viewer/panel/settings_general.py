"""Panel tab for configuring general plot settings.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import TAB_BAR_PADDING


import_export_button_styling = {
    'width': '100%',
    'textAlign': 'center',
    'fontWeight': 'bold',
}


def plot_settings_general():
    """Creates the configuration panel tab with general plot settings"""
    contents = [
        dash.html.H2(
            'General settings',
            style={'marginTop': TAB_BAR_PADDING},
        ),
        dash.html.Br(),
        dash.html.H4('Load/Save Plot Configuration'),
        dash.html.Br(),
        dbc.Row([
            dbc.Col(
                dash.dcc.Upload(
                    dbc.Button('Import', id='config-import-button',
                               style=import_export_button_styling),
                    id='plot-config-upload',
                ),
                class_name='d-grid gap-2',
            ),
            dbc.Col(
                [
                    dbc.Button('Export', id='config-export-button',
                               style=import_export_button_styling),
                    dash.dcc.Download(id='config-export-download'),
                ],
                class_name='d-grid gap-2',
            ),
        ]),
    ]

    return contents
