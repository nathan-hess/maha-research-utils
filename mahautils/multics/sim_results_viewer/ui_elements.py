"""User interface (UI) elements used throughout the SimViewer interface
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from .constants import COLOR_PICKER_STYLE


def color_picker(identifier, current_color: str):
    """An interactive element that allows the user to choose a color and
    displays the currently selected color"""
    return dbc.Row([
        dbc.Col(
            dbc.Input(
                id=identifier,
                type='color',
                value=current_color,
                style=COLOR_PICKER_STYLE,
            ),
            width=3,
        ),
        dbc.Col([
            dash.html.P(
                'Selected color hex code: ',
                style={'fontWeight': 'bold', 'marginBottom': '0px'}),
            dash.html.P(
                current_color,
                style={'fontFamily': 'monospace', 'marginTop': '0px'}),
        ]),
    ])


def on_off_switch_row(identifier, state: bool, description: str):
    """A row with a single on/off switch and a description"""
    return dbc.Row([
        dbc.Col(
            dbc.Switch(
                id=identifier,
                value=state,
            ),
            width=2,
        ),
        dbc.Col(
            dash.html.P(description),
            width=10,
        ),
    ])
