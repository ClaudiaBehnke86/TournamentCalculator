#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'matplotlib',
    'numpy>=1.15.4',
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Claudia Behnkea",
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
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ClaudiaBehnke86/TournamentCalculator',
    version='0.1.0',
    zip_safe=False,
)
