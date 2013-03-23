# -*- coding: utf-8 -*-
"""
lexington.testsuite.regex_impl
==============================
This file contains tests for the internals of the regular expression module.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
import unittest
from . import LexingtonTestCase, make_suite

from lexington.regex import (Regex, Null, Epsilon, Any, regexify,
                             concat, union, join, star,
                             EpsilonRegex, NullRegex, AnySymbolRegex,
                             SymbolRegex, ConcatRegex, UnionRegex, StarRegex)


class ConstructorTests(object):
    def test_regexify_symbol(self):
        pass


suite = make_suite(
    ConstructorTests
)
