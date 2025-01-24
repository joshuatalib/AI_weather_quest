# Configuration file for the Sphinx documentation builder.

import tomli  # Use 'import tomllib' if using Python 3.11+
from pathlib import Path

# -- Project information

project = 'AI_Weather_Quest'
copyright = '2025, Talib'
author = 'Joshua Talib'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_logo = 'docs/source/Logo_AIWQ_Dark.png'

# -- Options for EPUB output
epub_show_urls = 'footnote'
