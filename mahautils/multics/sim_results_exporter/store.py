"""Data structures for storing program data in the browser.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore


def export_config_store():
    """Creates browser session storage for information about which simulation
    results variables to export
    """
    return dash.dcc.Store(
        id='export-config-store',
        storage_type='session',
    )
