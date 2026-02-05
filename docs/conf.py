# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os

try:
    from tomllib import loads as load_toml
except ImportError:
    from toml import loads as load_toml

def get_project_metadata():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../pyproject.toml"))
    with open(path, "r") as f:
        return load_toml(f.read())['project']

metadata = get_project_metadata()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = metadata['name']
copyright = f'2026, {metadata["authors"][0]["name"]}'
author = metadata['authors'][0]['name']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.doctest',
    'sphinxcontrib.spelling'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = [
    # '_static'
]
