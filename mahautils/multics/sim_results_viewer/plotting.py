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
        dash.html.P('Upload your simulation results file here'),
        dash.dcc.Upload(
            'Drag and Drop a File',
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
        dash.html.Hr(),
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
