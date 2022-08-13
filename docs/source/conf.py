# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
import mahautils


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MahaUtils'
author = 'Nathan Hess'
copyright = f'{datetime.datetime.now().year}'
release = mahautils.__version__
url = 'https://github.com/nathan-hess/maha-research-utils'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings
extensions = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# HTML theme
html_theme = 'sphinx_book_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Site logo and favicon
html_logo = '_static/logo.svg'
html_favicon = '_static/favicon.ico'

# General HTML options
html_title = f'{project} v{release}'
html_last_updated_fmt = '%b %d, %Y'
html_permalinks = False
html_show_sourcelink = False
html_show_sphinx = False

# Theme-specific HTML options
html_theme_options = {
    'extra_navbar': '',
    'home_page_in_toc': False,
    'navigation_with_keys': False,
    'repository_url': url,
    'search_bar_text': 'Search site...',
    'use_repository_button': True,
}

html_sidebars = {
    '**': [
        'sidebar-logo.html',
        'search-field.html',
        'sbt-sidebar-nav.html',
    ]
}
