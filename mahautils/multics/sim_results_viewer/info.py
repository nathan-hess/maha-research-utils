"""Information box showing software version and credits.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import numpy as np
import plotly                            # type: ignore
import pyxx

from .constants import (
    GUI_LONG_NAME,
    GUI_SHORT_NAME,
    PROJECT_NAME,
    REPO_URL,
    VERSION,
)


def info_box():
    """Creates an "about" box showing program version and acknowledgements"""
    contents = [
        dbc.ModalHeader(
            dbc.ModalTitle(f'{PROJECT_NAME} {GUI_SHORT_NAME} v{VERSION}'),
            close_button=True,
        ),
        dbc.ModalBody([
            dash.html.P(
                [
                    (f'{PROJECT_NAME} is an open source project, and all '
                     'source code is available through '),
                    dash.html.A(
                        ['GitHub ', dash.html.I(className='bi bi-github')],
                        href=REPO_URL,
                        target='_blank',
                    ),
                    (f'.  The {PROJECT_NAME} {GUI_LONG_NAME} ({GUI_SHORT_NAME}) '
                     'graphical user interface is powered by '),
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
