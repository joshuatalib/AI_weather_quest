# Configuration file for the Sphinx documentation builder.

import tomli  # Use 'import tomllib' if using Python 3.11+
from pathlib import Path

# -- Project information

project = 'AI_Weather_Quest'
copyright = '2025, Talib'
author = 'Joshua Talib'

# Read version from pyproject.toml
pyproject_path = Path(__file__).parent.parent / "pyproject.toml"  # Adjust the path as needed
with pyproject_path.open("rb") as f:
    pyproject = tomli.load(f)

# Extract version from the relevant section (e.g., `[tool.poetry]` or `[project]`)
release = pyproject.get("tool", {}).get("poetry", {}).get("version", "0.0.0")  # For Poetry projects
# or
# release = pyproject.get("project", {}).get("version", "0.0.0")  # For PEP 621-compliant projects

version = ".".join(release.split(".")[:2])  # e.g., '0.1' for '0.1.0'

# release = '0.1'
# version = '0.1.0'

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

# -- Options for EPUB output
epub_show_urls = 'footnote'
