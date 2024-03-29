#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'numpy',
    'pandas',
    'plotly',
    'setuptools',
    'sphinx_rtd_theme',
    'streamlit'
]

ex_path = os.path.join('tourcalc', 'example_tours')

setup(
    author="Claudia Behnke",
    author_email='',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='tourcalc',
    name='tourcalc',
    packages=find_packages(include=['tourcalc']),
    package_data = {
	   ex_path: ['*.csv']
    },
    url='https://github.com/ClaudiaBehnke86/TournamentCalculator',
    version='0.9.0',
    zip_safe=False,
)
