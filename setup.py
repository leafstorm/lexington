#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
setup.py for Lexington
======================
:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
# intentionally not importing unicode_literals
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Load various pieces of information
with open("README.rst") as fd:
    README = fd.read()

packages = [
    "lexington",
    "lexington.testsuite"
]


setup(
    name='Lexington',
    version='0.1-dev',
    url='https://github.com/leafstorm/lexington',
    license='MIT/X11',
    description="A nonblocking lexer toolkit.",
    long_description=README,

    author='Matthew Frazier',
    author_email='leafstormrush@gmail.com',

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: General'
    ],

    packages=packages,
    zip_safe=False,

    test_suite='lexington.testsuite.suite'
)
