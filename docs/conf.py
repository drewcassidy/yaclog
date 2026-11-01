# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from datetime import datetime
import docput

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path


def include(file_path):
    docs_root = Path(__file__).parent.absolute()
    with open(docs_root / file_path, "r") as fp:
        return fp.read()


sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "Yaclog"
copyright = f"{datetime.now().year}, Andrew Cassidy"
author = "Andrew Cassidy"
ref = os.environ.get("YACLOG_GIT_REF", "main")  # overwritten when building docs in CI

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "docput",
    "myst_parser",
    "sphinx_click",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_gha",
    "sphinx_copybutton",
]

myst_heading_anchors = 2
myst_enable_extensions = ["colon_fence"]

# Add any paths that contain templates here, relative to this directory.
templates_path = [docput.sphinx_templates, "_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

default_role = "py:obj"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_logo = "docs_logo.png"
html_favicon = "favicon.ico"
html_title = f"{project} documentation"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/version-switch.html",
        "sidebar/search.html",
        "sidebar/navigation.html",
        "sidebar/scroll-end.html",
    ]
}
html_theme_options = {
    "source_edit_link": "https://git.offworld.city/drewcassidy/yaclog/_edit/main/docs/{filename}",
    "source_view_link": "https://git.offworld.city/drewcassidy/yaclog/src/branch/main/docs/{filename}?display=source",
    "footer_icons": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/yaclog",
            "html": include(Path("_include", "pypi-hover.svg")),
            "class": "",
        },
        {
            "name": "Source",
            "url": "https://git.offworld.city/drewcassidy/yaclog",
            "html": include(Path("_include", "forgejo-hover.svg")),
            "class": "",
        },
    ],
}

# -- Options for Autodoc -----------------------------------------------------

add_module_names = False
autodoc_docstring_signature = True
autoclass_content = "both"

autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": True,
}


# -- Options for Intersphinx -------------------------------------------------

# This config value contains the locations and names of other projects that
# should be linked to in this documentation.

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "packaging": ("https://packaging.pypa.io/en/latest/", None),
}

# -- Options for sphinx-gha --------------------------------------------------

sphinx_gha_repo_root = str(Path(__file__).parent.parent.absolute())  # docs/..
sphinx_gha_repo_slug = "https://git.offworld.city/drewcassidy/yaclog"
sphinx_gha_repo_ref = ref

# -- Options for sphinx-copybutton -------------------------------------------
copybutton_prompt_text = "$"
