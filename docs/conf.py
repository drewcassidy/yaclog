# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from importlib.metadata import version

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'Yaclog'
copyright = '2021, Andrew Cassidy'
author = 'Andrew Cassidy'
release = version('yaclog')
version = '.'.join(release.split('.')[:3])
ref = version if len(release.split('.')) == 3 else 'main'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser',
    'sphinx_click',
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_jinja'
]

myst_heading_anchors = 2
myst_enable_extensions = [
    "colon_fence"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

default_role = 'py:obj'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_logo = 'docs_logo.png'
html_favicon = 'favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['css/custom.css']

# -- Options for Autodoc -----------------------------------------------------

add_module_names = False
autodoc_docstring_signature = True
autoclass_content = 'both'

autodoc_default_options = {
    'member-order': 'bysource',
    'undoc-members': True,
}



# -- Options for Intersphinx -------------------------------------------------

# This config value contains the locations and names of other projects that
# should be linked to in this documentation.

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'packaging': ('https://packaging.pypa.io/en/latest/', None),
}

jinja_globals = {
    'version': version,
    'release': release,
    'ref': ref,
}