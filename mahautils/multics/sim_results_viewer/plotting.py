"""Code for the components of the simulation results viewer that generate and
modify the data graph.
"""

# Mypy type checking is disabled for several packages because they are not
# PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore


def _graph():
    default_height_percent = 90

    contents = dash.dcc.Graph(
        id='plotly-graph',
        style={
            'height': f'{default_height_percent}vh',
        },
    )

    return contents


def _plot_controls():
    default_width_percent = 45
    default_open = True

    contents = [
        dash.html.H5('Data Upload'),
        dash.html.P('Upload a new simulation results file here.'),
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
                'margin-left': '0px',
                'margin-right': '0px',
            },
        ),
        dash.html.Div(
            dbc.Row([
                dbc.Col(
                    dbc.Input(
                        placeholder='Enter a name for your file...',
                        id='user-file-name',
                    ),
                    width=9, style={'margin-top': '10px'},
                ),
                dbc.Col(
                    dbc.Button('Load', id='load-file-button'),
                    width=3, style={'margin-top': '10px'},
                ),
            ]),
            id='div-user-file-name',
        ),
        dash.html.Hr(),
        dash.html.H5('Current Files'),
        dash.html.P('Manage your uploaded simulation results files here.'),
        dbc.Table(
            [
                dash.html.Thead(dash.html.Tr([
                    dash.html.Th('Enabled', style={'width': '15%'}),
                    dash.html.Th('Name', style={'width': '70%'}),
                    dash.html.Th('Delete', style={'width': '15%'}),
                ])),
                dash.html.Tbody(id='file-list-table-body'),
            ],
        ),
    ]

    return dbc.Offcanvas(
        contents,
        id='plot-config-panel',
        title='Plot Settings',
        placement='end',
        is_open=default_open,
        style={
            'width': f'{default_width_percent}vw',
        },
    )
