"""Code for generating the header of the simulation results viewer.
"""

# Mypy type checking is disabled for several packages because they are not
# PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore


def _app_header():
    """Creates a formatted header for the application"""
    contents = [
        dbc.Stack([
            # Left side of header: app name
            dbc.Row([
                dash.html.H1(
                    'MahaUtils Simulation Results Viewer',
                    style={
                        'font-size': 24,
                        'margin-left': '10px',
                        'margin-right': '10px',
                    },
                ),
            ]),

            # Right side of header: buttons to open plot configuration pane
            # and app information box
            dbc.Row(
                dash.html.Div(
                    [
                        dash.html.Button(
                            dash.html.I(className='fa fa-wrench'),
                            id='plot-config-button',
                            style={
                                'height': '32px',
                                'width': '32px',
                                'border-radius': '8px',
                                'text-align': 'center',
                                'margin-left': '10px',
                                'margin-right': '2px',
                            },
                        ),
                        dash.html.Button(
                            dash.html.I(className='fa fa-question-circle'),
                            id='info-button',
                            style={
                                'height': '32px',
                                'width': '32px',
                                'border-radius': '8px',
                                'text-align': 'center',
                                'margin-left': '2px',
                                'margin-right': '10px',
                            },
                        ),
                    ],
                ),
                style={
                    'margin-left': 'auto',
                    'margin-right': '0px',
                },
            ),
        ], direction='horizontal'),

        # Horizontal line below title
        dash.html.Hr(),
    ]

    return dbc.Row(children=contents)
