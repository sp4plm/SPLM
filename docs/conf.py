# -*- coding: utf-8 -*-

import sys
import os

pth = os.path.abspath("../app")

project_root = os.path.dirname(os.getcwd())
sys.path.insert(0, pth)



extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.autosectionlabel', 'sphinx.ext.coverage', 'sphinx.ext.napoleon']

autodoc_mock_imports = ['flask', 'pickle', 'configparser', 'rdflib', 'requests', 'subprocess', 'os', 'sys', 'app']


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'splm'
copyright = '2022, sp4plm'
author = 'sp4plm'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

pygments_style = 'sphinx'

source_suffix = '.rst'

exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


