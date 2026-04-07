"""Sphinx configuration for Healthcare VOC Compliance documentation."""

project = 'Healthcare VOC Compliance'
copyright = '2026, Dave Cook / Binx Professional Cleaning'
author = 'Dave Cook'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build']

html_theme = 'alabaster'
html_theme_options = {
    'description': 'VOC compliance calculator and datasets for healthcare facility cleaning.',
    'github_user': 'DaveCookVectorLabs',
    'github_repo': 'healthcare-voc-compliance',
    'github_button': True,
    'extra_nav_links': {
        'Binx Professional Cleaning': 'https://www.binx.ca/commercial.php',
        'PyPI': 'https://pypi.org/project/healthcare-voc-compliance/',
        'Datasets': 'https://huggingface.co/datasets/davecook1985/healthcare-voc-compliance',
    },
}

html_static_path = ['_static']
