# http://www.sphinx-doc.org/en/master/config
import os
import sys

# -- Path setup --------------------------------------------------------------

sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'PS3ISO'
copyright = '2019, Joshua Stover'
author = 'Joshua Stover'


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.apidoc',
    'sphinxcontrib.autoprogram',
    'sphinxcontrib.fulltoc',
    'sphinx_autodoc_typehints',
    'sphinx_git',
    'sphinx_sitemap',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Add any paths that contain custom static files (such as style sheets) here,
html_static_path = ['_static']

# Source file/directory patterns to ignore. Relative to source directory
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
html_theme = 'nature'
#import sphinx_glpi_theme as theme_module
#html_theme_path = [theme_module.get_html_themes_path()]

# Set for sphinx-sitemap when deploying
#html_baseurl = 'https://example.com/docs/'


# -- Apidoc setup ------------------------------------------------------------

apidoc_module_dir = '../../ps3iso'
apidoc_output_dir = 'apidoc'
apidoc_excluded_paths = ['']
apidoc_separate_modules = False
apidoc_toc_file = False
apidoc_module_first = True

