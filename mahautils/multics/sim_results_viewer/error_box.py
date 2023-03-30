"""Function for generating pop-up error boxes"""

from typing import Dict

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore


def error_box(identifier: Dict[str, str]):
    """Creates a pop-up box for displaying error messages"""
    text_id = {k: (v + '-text') for k, v in identifier.items()}

    contents = [
        dbc.ModalHeader(
            dbc.ModalTitle(
                dash.html.H4([
                    dash.html.I(className='fa fa-exclamation-triangle'),
                    ' Error',
                ], style={'color': 'red'})),
            close_button=True,
        ),
        dbc.ModalBody(dash.html.Div(id=text_id)),
    ]

    return dbc.Modal(
        contents,
        id=identifier,
        scrollable=True,
        size='lg',
        is_open=False,
    )


def generate_error_box_text(message, exception: Exception):
    """Generates error box text, beginning with a user-specified error message
    followed by the Python exception message"""
    return [
        message,
        dash.html.Br(),
        dash.html.P('Debugging Details', style={'fontWeight': 'bold'}),
        dash.html.P('Here is the exception that triggered this error:'),
        dash.html.P(f'{exception.__class__.__name__}: {exception}',
                    style={'fontFamily': 'monospace'})
    ]
