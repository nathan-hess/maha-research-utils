"""Default settings and templates for creating plots for the
:py:mod:`mahautils.shapes` module.
"""

from typing import Optional

# Mypy type checking disabled for packages that are not PEP 561-compliant
import plotly.graph_objects as go  # type: ignore

_figure_config = {
    'edits': {
        'annotationPosition': True,
        'annotationTail': True,
        'annotationText': True,
        'legendPosition': True,
    },
    'modeBarButtonsToAdd': [
        'drawclosedpath',
        'drawopenpath',
        'drawline',
        'drawrect',
        'drawcircle',
        'eraseshape',
    ],
    'toImageButtonOptions': {
        'format': 'png',
        'width': None,
        'height': None,
    },
    'scrollZoom': True,
    'showAxisDragHandles': True,
}


def _create_blank_plotly_figure(units: Optional[str] = None):
    """Creates a blank Plotly figure with general formatting options, intended
    to be used to plot :py:class:`mahautils.shapes.Layer` and
    :py:class:`mahautils.shapes.Canvas` objects

    Parameters
    ----------
    units : str, optional
        Units to display in axis titles, or ``None`` to suppress showing units
        in axis titles (default is ``None``)
    """
    figure = go.Figure()

    # Axis titles
    if units is None:
        figure.update_layout(xaxis_title='x')
        figure.update_layout(yaxis_title='y')
    else:
        figure.update_layout(xaxis_title=f'x [{units}]')
        figure.update_layout(yaxis_title=f'y [{units}]')

    # Use equal scale for x- and y-axes
    figure.update_yaxes(scaleanchor='x', scaleratio=1)

    # Default format settings
    figure.update_layout(margin={'t': 30, 'r': 20})

    default_axes_settings = {
        # Border around plot
        'showline': True, 'linewidth': 1, 'linecolor': 'black', 'mirror': True,

        # Settings for x=0 and y=0 axes
        'zeroline': True, 'zerolinewidth': 1, 'zerolinecolor': '#7b7b7b',

        # Settings for gridlines
        'showgrid': True, 'gridwidth': 1, 'gridcolor': '#d2d2d2',
    }
    figure.update_xaxes(**default_axes_settings)
    figure.update_yaxes(**default_axes_settings)

    figure.update_layout(plot_bgcolor='white')

    # Hide legend
    figure.update_layout(showlegend=False)

    return figure
