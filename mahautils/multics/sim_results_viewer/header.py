"""Code for generating the header of the simulation results viewer.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from .constants import GUI_SHORT_NAME, PROJECT_NAME, VERSION


def app_header():
    """Creates a formatted header for the application"""
    contents = [
        dbc.Stack([
            # Left side of header: app name
            dbc.Row([
                dash.html.H1(
                    f'{PROJECT_NAME} {GUI_SHORT_NAME} v{VERSION}',
                    style={
                        'fontSize': 24,
                        'marginLeft': '10px',
                        'marginRight': '10px',
                    },
                ),
            ]),

            # Right side of header: buttons to open plot configuration pane
            # and app information box
            dbc.Row(
                dash.html.Div(
                    [
                        dbc.Button(
                            dash.html.I(className='fa fa-wrench'),
                            id='plot-config-button',
                            size='sm',
                            style={
                                'borderRadius': '8px',
                                'marginTop': '5px',
                                'marginLeft': '10px',
                                'marginRight': '2px',
                                'marginBottom': '5px',
                            },
                        ),
                        dbc.Button(
                            dash.html.I(className='fa fa-question-circle'),
                            id='info-button',
                            size='sm',
                            style={
                                'borderRadius': '8px',
                                'marginTop': '5px',
                                'marginLeft': '2px',
                                'marginRight': '10px',
                                'marginBottom': '5px',
                            },
                        ),
                    ],
                ),
                style={
                    'marginLeft': 'auto',
                    'marginRight': '0px',
                },
            ),
        ], direction='horizontal'),

        # Horizontal line below title
        dash.html.Hr(),
    ]

    return dbc.Row(children=contents)
