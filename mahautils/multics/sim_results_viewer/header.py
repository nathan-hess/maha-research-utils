"""Code for generating the header of the simulation results viewer.
"""

import dash
import dash_bootstrap_components as dbc

from mahautils import __version__ as VERSION

REPO_URL = 'https://github.com/nathan-hess/maha-research-utils'


def _app_header():
    """Creates a formatted header for the application"""
    contents = [
        dbc.Stack([
            # Left side of header: app name
            dbc.Row([
                dash.html.H1(
                    'Maha Multics Simulation Results Viewer',
                    style={
                        'font-size': 24,
                        'margin-left': '10px',
                        'margin-right': '10px',
                    },
                ),
            ]),

            # Right side of header: version and link to repository
            dbc.Stack([
                dash.html.Div(
                    f'v{VERSION}',
                    style={
                        'font-size': 12,
                        'color': 'gray',
                        'margin-left': '10px',
                        'margin-right': '10px',
                        'text-align': 'right',
                    },
                ),
                dash.html.A(
                    ['Source Code ', dash.html.I(className='bi bi-github')],
                    href=REPO_URL,
                    target='_blank',
                    style={
                        'font-size': 12,
                        'color': 'gray',
                        'margin-left': '10px',
                        'margin-right': '10px',
                        'text-align': 'right',
                    },
                ),
            ]),
        ], direction='horizontal'),

        # Horizontal line below title
        dash.html.Hr(),
    ]

    return dbc.Row(children=contents)
