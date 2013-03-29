# -*- coding: utf-8 -*-
"""
lexington.testsuite.run
=======================
This is the entry point for Lexington's test suite.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
# intentionally not importing unicode_literals
import sys
import unittest
from . import suite

if '-h' in sys.argv or '-H' in sys.argv or '--help' in sys.argv:
    print("Options: -q, --quiet, -v, --verbose")
    sys.exit(1)

if '-q' in sys.argv or '--quiet' in sys.argv:
    verbosity = 0
elif '-v' in sys.argv or '--verbose' in sys.argv:
    verbosity = 2
else:
    verbosity = 1

test_suite = suite()
runner = unittest.TextTestRunner(verbosity=verbosity)
result = runner.run(test_suite)

sys.exit(0 if result.wasSuccessful() else 1)
