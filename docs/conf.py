# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'VRPSolverEasy'
copyright = '2023, ERRAMI Najib SADYKOV Ruslan UCHOA Eduardo QUEIROGA Eduardo'
author = 'ERRAMI Najib SADYKOV Ruslan UCHOA Eduardo QUEIROGA Eduardo'
release = '0.1.3'

import sys, os

#find module solver-----------------------------------------------------------
sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../VRPSolverEasy"))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc",
              "sphinx.ext.mathjax",
              'sphinx.ext.autosummary',
              'sphinxcontrib.bibtex']


bibtex_bibfiles = ['Bibliography/refs.bib']

templates_path = []
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = []
