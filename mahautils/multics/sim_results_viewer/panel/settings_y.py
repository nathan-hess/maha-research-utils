"""Panel tab for configuring y-axis plot settings.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash                              # type: ignore
import dash_bootstrap_components as dbc  # type: ignore

from mahautils.multics.sim_results_viewer.constants import (
    SIM_RESULTS_DICT_T,
    TAB_BAR_PADDING,
    UI_DESCRIPTION_MARGIN_BELOW,
)
from mahautils.multics.sim_results_viewer.store import (
    default_plot_config_y,
    default_trace_settings,
    default_y_axis_settings,
)
from mahautils.multics.sim_results_viewer.ui_elements import (
    color_picker,
    numbered_item_selector,
    tick_range_step,
)


def plot_settings_y():
    """Creates the configuration panel tab with settings for the y-axes"""
    return [
        dash.html.Div(
            render_y_settings(default_plot_config_y, {}, {}, 1, 1),
            id='plot-config-y-settings',
            style={'marginTop': TAB_BAR_PADDING},
        ),
    ]


def render_y_settings(config_y: dict, sim_results_files: SIM_RESULTS_DICT_T,
                      file_metadata: dict,
                      selected_axis: int, selected_data_series: int):
    """Generates the UI elements that allow the user to configure y-axis
    plot settings"""
    # Extract axis data
    num_axes = len(config_y['axes'])
    is_axis_selected = (num_axes != 0)

    axis = config_y['axes'][selected_axis] if num_axes > 0 \
        else default_y_axis_settings

    # Extract data series/trace data
    num_traces = len(axis['traces'])
    is_trace_selected = (num_traces != 0)

    trace = axis['traces'][selected_data_series] if num_traces > 0 \
        else default_trace_settings

    file_enabled = ((trace['file'] in file_metadata)
                    and file_metadata[trace['file']]['enabled'])

    return [
        # Axis selector and buttons for creating and deleting axes
        dash.html.H5('Y-Axis Selector', style={'marginBottom': '10px'}),
        numbered_item_selector(
            pagination_id='y-axis-selector',
            add_button_id='add-y-axis-button',
            hide_show_button_id='hide-show-y-axis-button',
            delete_button_id='delete-y-axis-button',
            name='y-axis',
            name_plural='y-axes',
            num_items=num_axes,
            active_page=selected_axis+1,
            is_active_page_shown=axis['enabled'],
        ),

        # Selected axis properties
        dash.html.Div([
            # Axis formatting options
            dash.html.H4('Formatting'),
            dash.html.Hr(),
            dash.html.H5('Axis Title'),
            dbc.Input(
                debounce=True,
                id={'component': 'plot-config', 'tab': 'y',
                    'field': 'title'},
                placeholder='Enter a title for the y-axis...',
                value=axis['axis_title'],
            ),
            dash.html.Br(),
            dash.html.H5('Axis Color'),
            color_picker(
                identifier={'component': 'plot-config', 'tab': 'y',
                            'field': 'axis-color'},
                current_color=axis['color'],
            ),
            dash.html.Br(),
            tick_range_step(
                range_min_id={'component': 'plot-config', 'tab': 'y',
                              'field': 'ymin'},
                range_max_id={'component': 'plot-config', 'tab': 'y',
                              'field': 'ymax'},
                tick_spacing_id={'component': 'plot-config', 'tab': 'y',
                                 'field': 'tick_spacing'},
                range_min_val=axis['ymin'],
                range_max_val=axis['ymax'],
                tick_spacing_val=axis['tick_spacing'],
            ),
            dash.html.Br(),
            dash.html.Br(),

            # Axis data/traces selection
            dash.html.H4('Data Series Configuration'),
            dash.html.Hr(),
            numbered_item_selector(
                pagination_id='y-data-selector',
                add_button_id='add-y-data-button',
                hide_show_button_id='hide-show-y-data-button',
                delete_button_id='delete-y-data-button',
                name='data series',
                name_plural='data series',
                num_items=num_traces,
                active_page=selected_data_series+1,
                is_active_page_shown=trace['enabled'],
                disable_hide_show_button=(not file_enabled),
            ),
            dash.html.Div([
                dash.html.Div(
                    [
                        dash.html.P(
                            'The show/hide controls for this data series are '
                            'disabled because the file has been disabled on the '
                            '"Data Files" tab.  You can edit the settings '
                            'below, but the data series will not be displayed '
                            'in the plot until you enable the file.',
                            style={'fontStyle': 'italic'},
                        ),
                        dash.html.Br(),
                    ],
                    hidden=file_enabled,
                ),
                dash.html.H5('Legend Title'),
                dbc.Input(
                    debounce=True,
                    id={'component': 'plot-config', 'tab': 'y',
                        'field': 'legend-title'},
                    placeholder='Enter a legend title for the data series...',
                    value=trace['name'],
                ),
                dash.html.Br(),
                dash.html.H5('Simulation Results File'),
                dash.dcc.Dropdown(
                    options=list(sim_results_files.keys()),
                    value=trace['file'],
                    id={'component': 'plot-config', 'tab': 'y',
                        'field': 'trace-file'},
                    clearable=True,
                    multi=False,
                ),
                dash.html.Br(),
                dash.html.H5('Simulation Results Variable'),
                dash.html.Div(dbc.Row([
                    dbc.Col(
                        dash.html.H6('Variable'),
                        width=2,
                    ),
                    dbc.Col(
                        dash.dcc.Dropdown(
                            options=(
                                [] if trace['file'] in (None, '')
                                else list(
                                    sim_results_files[trace['file']].variables)
                            ),
                            value=trace['variable'],
                            id={'component': 'plot-config', 'tab': 'y',
                                'field': 'trace-variable'},
                            clearable=True,
                            disabled=(trace['file'] in (None, '')),
                            multi=False,
                        ),
                        width=10,
                    ),
                ]), style={'marginBottom': UI_DESCRIPTION_MARGIN_BELOW}),
                dbc.Row([
                    dbc.Col(
                        dash.html.H6('Units'),
                        width=2,
                    ),
                    dbc.Col(
                        dbc.Input(
                            debounce=True,
                            value=trace['units'],
                            id={'component': 'plot-config', 'tab': 'y',
                                'field': 'units'},
                            disabled=(trace['file'] in (None, '')),
                            style={'width': 150},
                        ),
                        width=10,
                    ),
                ]),
                dash.html.Br(),
                dash.html.H5('Line Color'),
                color_picker(
                    identifier={'component': 'plot-config', 'tab': 'y',
                                'field': 'trace-color'},
                    current_color=trace['style']['color'],
                ),
                dash.html.Br(),
                dash.html.H5('Line Width'),
                dbc.Input(
                    debounce=True,
                    id={'component': 'plot-config', 'tab': 'y',
                        'field': 'trace-width'},
                    value=trace['style']['width'],
                ),
                dash.html.Br(),
                dash.html.H5('Line Style'),
                dash.dcc.Dropdown(
                    options=['solid', 'dot', 'dash', 'longdash',
                             'dashdot', 'longdashdot'],
                    value=trace['style']['dash'],
                    id={'component': 'plot-config', 'tab': 'y',
                        'field': 'trace-dash'},
                    clearable=False,
                    multi=False,
                ),
            ], hidden=(not is_trace_selected)),
        ], hidden=(not is_axis_selected))
    ]
