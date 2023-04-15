"""User interface (UI) elements used throughout the SimViewer interface
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from .constants import COLOR_PICKER_STYLE, UI_DESCRIPTION_MARGIN_BELOW


## COLOR PICKER ##

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


## NUMBERED ITEM SELECTOR ##

_selector_button_style = {
    'borderRadius': '8px',
    'marginTop': '2px',
    'marginLeft': '6px',
    'marginRight': '0px',
    'marginBottom': '2px',
    'width': '45px',
}


def numbered_item_selector(pagination_id, add_button_id,
                           hide_show_button_id, delete_button_id,
                           name: str, name_plural: str,
                           num_items: int, active_page: int,
                           is_active_page_shown: bool,
                           disable_hide_show_button: bool = False):
    """A set of elements for creating and managing a numbered set of items

    This function creates a :py:class:`dbc.Pagination` object that can be
    used to select numbered items, as well as associated buttons for adding,
    deleting, and hiding/showing items.
    """
    axis_exists = (num_items != 0)

    return dash.html.Div([
        dbc.Row([
            dbc.Col(
                [
                    dash.html.Div(
                        dbc.Pagination(
                            id=pagination_id,
                            min_value=1, max_value=num_items,
                            fully_expanded=False,
                            first_last=False,
                            previous_next=True,
                            active_page=active_page,
                        ),
                        hidden=(not axis_exists),
                    ),
                    dash.html.Div(
                        dash.html.P(
                            f'No {name_plural} created yet.  Click the "+" '
                            f'button to right to create a new {name}.'),
                        hidden=axis_exists,
                    ),
                ],
                xs=4, sm=4, md=5, lg=6, xl=7, xxl=8,
            ),
            dbc.Col(
                dash.html.Div(
                    [
                        dbc.Button(
                            dash.html.I(className='fa-sharp fa-solid fa-plus'),
                            id=add_button_id,
                            size='md',
                            n_clicks=0,
                            style=_selector_button_style,
                        ),
                        dbc.Button(
                            dash.html.I(
                                className=(
                                    'fa fa-eye-slash' if is_active_page_shown
                                    else 'fa fa-eye'),
                            ),
                            id=hide_show_button_id,
                            size='md',
                            n_clicks=0,
                            style=_selector_button_style,
                            disabled=(
                                disable_hide_show_button or (not axis_exists)
                            ),
                        ),
                        dbc.Button(
                            dash.html.I(className='bi bi-trash'),
                            id=delete_button_id,
                            color='danger',
                            size='md',
                            n_clicks=0,
                            style=_selector_button_style,
                            disabled=(not axis_exists),
                        ),
                    ],
                    style={'textAlign': 'right'}
                ),
            ),
        ], style={'marginBottom': '0px'}),
        dbc.Tooltip(f'Select a {name} to edit', target=pagination_id,
                    trigger='hover'),
        dbc.Tooltip(f'Add a new {name}', target=add_button_id, trigger='hover'),
        dbc.Tooltip(f'{"Hide" if is_active_page_shown else "Show"} the '
                    f'currently selected {name}',
                    target=hide_show_button_id, trigger='hover'),
        dbc.Tooltip(f'Delete the currently selected {name}',
                    target=delete_button_id,
                    trigger='hover'),
        dash.html.Hr(style={'marginTop': '0px'}),
    ])


## ON/OFF SWITCH ##

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


## TICK MARK OPTIONS ##

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
