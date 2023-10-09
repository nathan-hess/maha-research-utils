"""Data structures for storing program data in the browser.
"""

# Mypy type checking disabled for packages that are not PEP 561-compliant
import dash  # type: ignore


def app_settings_store(lite_mode: bool = False):
    """Creates browser session storage for information about app configuration
    """
    return dash.dcc.Store(
        id='app-settings-store',
        storage_type='session',
        data={'lite': lite_mode},
    )


def export_config_store():
    """Creates browser session storage for information about which simulation
    results variables to export
    """
    return dash.dcc.Store(
        id='export-config-store',
        storage_type='session',
    )
