"""User interface (UI) elements used throughout the SimViewer interface
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from .constants import COLOR_PICKER_STYLE, UI_DESCRIPTION_MARGIN_BELOW


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


def tick_range_step(range_min_id, range_max_id, tick_spacing_id,
                    range_min_val, range_max_val, tick_spacing_val):
    """Input boxes where users can select the range and tick spacing for
    plot axes"""
    return dash.html.Div([
        dash.html.H5('Axis Range'),
        dash.html.P(
            ('Sets the minimum and/or maximum axis limits.  Leave blank to '
             'automatically scale the axis'),
            style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW},
        ),
        dash.html.Div([
            dbc.Input(
                debounce=True,
                id=range_min_id,
                value=range_min_val,
                style={'display': 'inline-block', 'width': '100px'},
            ),
            dash.html.P('  —  ', style={'display': 'inline-block',
                                        'whiteSpace': 'pre'}),
            dbc.Input(
                debounce=True,
                id=range_max_id,
                value=range_max_val,
                style={'display': 'inline-block', 'width': '100px'},
            ),
        ]),
        dash.html.Br(),
        dash.html.H5('Tick Spacing'),
        dash.html.P(
            ('Sets the distance between tick marks.  Leave blank to '
             'automatically scale the tick spacing'),
            style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW},
        ),
        dbc.Input(
            debounce=True,
            id=tick_spacing_id,
            value=tick_spacing_val,
            style={'width': '100px'},
        ),
    ])
