# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import datetime
from importlib import metadata

# Custom constants (no Sphinx configuration)

REPOSITORY_URL = "https://github.com/aeisenbarth/myst-nb-json"

# -- Project information ---------------------------------------------------------------------------

project = "MyST-NB JSON"
author = "Andreas Eisenbarth"

copyright = f"{datetime.now():%Y}, Andreas Eisenbarth"

release = version = metadata.version("myst-nb-json")

# -- General configuration -------------------------------------------------------------------------

extensions = ["myst_nb"]

# List of glob-style patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# Myst-nb creates a folder "jupyter_execute" and copies notebooks there, which causes recursive
# inclusion, so exclude it. See https://github.com/executablebooks/MyST-NB/issues/129
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "jupyter_execute"]

# -- Options for HTML output -----------------------------------------------------------------------

html_theme = "sphinx_book_theme"

html_theme_options = dict(
    use_repository_button=True,
    use_download_button=False,
    repository_provider="gitlab",
    repository_url=REPOSITORY_URL,
    repository_branch="main",
    navigation_with_keys=False,  # https://github.com/pydata/pydata-sphinx-theme/issues/1492
    collapse_navbar=False,
    show_navbar_depth=1,
)

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["static"]

# Define custom CSS rules
html_css_files = ["custom.css"]

# If true, “Created using Sphinx” is shown in the HTML footer. Default is True.
html_show_sphinx = False

# -- myst_parser / myst_nb -------------------------------------------------------------------------
