"""Information box showing software version and credits.
"""

import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly
import pyxx

from mahautils import __version__ as VERSION

REPO_URL = 'https://github.com/nathan-hess/maha-research-utils'


def _info_box():
    contents = [
        dbc.ModalHeader(
            dbc.ModalTitle(f'MahaUtils SimViewer v{VERSION}'),
            close_button=True,
        ),
        dbc.ModalBody([
            dash.html.P(
                [
                    ('MahaUtils is an open source project, and all source '
                     'code is available through '),
                    dash.html.A(
                        ['GitHub ', dash.html.I(className='bi bi-github')],
                        href=REPO_URL,
                        target='_blank',
                    ),
                    '.  Graphical user interface powered by ',
                    dash.html.A(
                        'Dash',
                        href='https://plotly.com/dash/',
                        target='_blank',
                    ),
                    '.',
                ]
            ),
            dash.html.Br(),
            dash.html.P('Dependency versions:'),
            dash.html.Ul([
                dash.html.Li(f'Dash: v{dash.__version__}'),
                dash.html.Li(f'Dash Bootstrap Components: v{dbc.__version__}'),
                dash.html.Li(f'NumPy: v{np.__version__}'),
                dash.html.Li(f'Plotly: v{plotly.__version__}'),
                dash.html.Li(f'PyXX: v{pyxx.__version__}'),
            ]),
        ]),
        dbc.ModalFooter(
            dbc.Button(
                'Close',
                id='info-box-close-button',
            ),
        ),
    ]

    return dbc.Modal(
        contents,
        id='info-button-modal',
        scrollable=True,
        size='lg',
        is_open=False,
    )
