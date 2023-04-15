"""Panel tab for configuring general plot settings.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import (
    TAB_BAR_PADDING,
    UI_DESCRIPTION_MARGIN_BELOW,
)
from mahautils.multics.sim_results_viewer.store import default_plot_config_general
from mahautils.multics.sim_results_viewer.ui_elements import (
    color_picker,
    on_off_switch_row,
)


import_export_button_styling = {
    'width': '100%',
    'textAlign': 'center',
    'fontWeight': 'bold',
}


def plot_settings_general():
    """Creates the configuration panel tab with general plot settings"""
    return [
        dash.html.H4('Load/Save Plot Configuration',
                     style={'marginTop': TAB_BAR_PADDING},),
        dash.html.Hr(),
        dbc.Row([
            dbc.Col(
                dbc.Spinner(
                    dash.dcc.Upload(
                        dbc.Button('Import', id='config-import-button',
                                   style=import_export_button_styling),
                        id='plot-config-upload',
                    ),
                    # Delay prevents showing spinner when changing other
                    # configuration UI elements
                    delay_show=200,
                ),
                class_name='d-grid gap-2',
            ),
            dbc.Col(
                [
                    dbc.Button('Export', id='config-export-button',
                               style=import_export_button_styling),
                    dash.dcc.Download(id='config-export-download'),
                ],
                class_name='d-grid gap-2',
            ),
        ]),
        dash.html.Br(),
        dash.html.Br(),
        dash.html.Div(
            render_general_settings(default_plot_config_general),
            id='plot-config-general-settings'
        ),
    ]


def render_general_settings(config_general: dict):
    """Generates the UI elements that allow the user to configure general
    plot settings"""
    return [
        dash.html.H4('Plot Appearance'),
        dash.html.Hr(),
        dash.html.H5('Plot Title'),
        dbc.Input(
            debounce=True,
            id={'component': 'plot-config', 'tab': 'general',
                'field': 'title'},
            placeholder='Enter a title for the plot...',
            value=config_general['title'],
        ),
        dash.html.Br(),
        dash.html.H5('Background Color'),
        color_picker(
            identifier={'component': 'plot-config', 'tab': 'general',
                        'field': 'background-color'},
            current_color=config_general['background_color'],
        ),
        dash.html.Br(),
        dash.html.H5('Gridlines'),
        on_off_switch_row(
            identifier={'component': 'plot-config', 'tab': 'general',
                        'field': 'grid-x'},
            state=config_general['grid_x'],
            description='Enable x-axis gridlines'),
        on_off_switch_row(
            identifier={'component': 'plot-config', 'tab': 'general',
                        'field': 'grid-y'},
            state=config_general['grid_y'],
            description='Enable y-axis gridlines'),
        dash.html.Br(),
        dash.html.H5('Units'),
        on_off_switch_row(
            identifier={'component': 'plot-config', 'tab': 'general',
                        'field': 'append-units'},
            state=config_general['append_units'],
            description=('Append units to axis titles and legend entries '
                         '(where applicable)')),
        dash.html.Br(),
        dash.html.H5('Vertical Axis Spacing'),
        dash.html.P(
            ('Sets the width in the plot window allocated for each vertical '
             'y-axis.  Must be a number in the range [0, 1]'),
            style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW},
        ),
        dbc.Input(
            debounce=True,
            value=config_general['width_per_y_axis'],
            id={'component': 'plot-config', 'tab': 'general',
                'field': 'width-per-y-axis'},
            style={'width': 200},
        ),
        dash.html.Br(),
        dash.html.Br(),
        dash.html.H4('User Interface'),
        dash.html.Hr(),
        dash.html.H5('Hover Labels'),
        dash.html.P(
            ('Controls the information displayed when hovering the cursor '
             'over the plot'),
            style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW},
        ),
        dash.dcc.Dropdown(
            options=['closest', 'x unified', 'y unified', 'x', 'y'],
            value=config_general['hovermode'],
            id={'component': 'plot-config', 'tab': 'general',
                'field': 'hovermode'},
            clearable=False,
            multi=False,
        ),
        dash.html.Br(),
        dash.html.H5('Plot Updates'),
        on_off_switch_row(
            identifier={'component': 'plot-config', 'tab': 'general',
                        'field': 'freeze-uirevision'},
            state=config_general['freeze_uirevision'],
            description='Prevent user interface state reset on plot updates'),
        dbc.Tooltip(
            ('Prevents changes to plot data or settings from resetting past '
             'user interactions (zoom, clicking legend items, shape '
             'annotations, etc.)'),
            target={'component': 'plot-config', 'tab': 'general',
                    'field': 'freeze-uirevision'},
            trigger='hover',
        ),
        dash.html.Br(),
        dash.html.Br(),
        dash.html.H4('Image Export Options'),
        dash.html.Hr(),
        dash.html.H5('Export Type'),
        dash.dcc.Dropdown(
            options=['png', 'jpeg', 'webp', 'svg'],
            value=config_general['image_export_type'],
            id={'component': 'plot-config', 'tab': 'general',
                'field': 'image_export_type'},
            clearable=False,
            multi=False,
        ),
        dash.html.Br(),
        dash.html.H5('Aspect Ratio'),
        dash.html.P(
            ('Output aspect ratio for exported images (width x height). '
             'Leave blank to use window size'),
            style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW},
        ),
        dash.html.Div([
            dbc.Input(
                debounce=True,
                id={'component': 'plot-config', 'tab': 'general',
                    'field': 'image_export_width'},
                value=config_general['image_export_width'],
                style={'display': 'inline-block', 'width': '100px'},
            ),
            dash.html.P('  x  ', style={'display': 'inline-block',
                                        'whiteSpace': 'pre'}),
            dbc.Input(
                debounce=True,
                id={'component': 'plot-config', 'tab': 'general',
                    'field': 'image_export_height'},
                value=config_general['image_export_height'],
                style={'display': 'inline-block', 'width': '100px'},
            ),
        ]),
        dash.html.Br(),
        dash.html.H5('Resolution'),
        dash.html.P(
            ('Setting this to n will increase the exported image '
             'resolution by a factor of n'),
            style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW},
        ),
        dbc.Input(
            debounce=True,
            id={'component': 'plot-config', 'tab': 'general',
                'field': 'image_export_scale'},
            value=config_general['image_export_scale'],
            style={'width': '100px'},
        ),
    ]
