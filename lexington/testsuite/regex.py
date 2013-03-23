# -*- coding: utf-8 -*-
"""
lexington.testsuite.regex
=========================
This file contains API-level tests for the regular expression module.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
import unittest
from . import LexingtonTestCase, make_suite

from lexington.regex import (Regex, Null, Epsilon, Any,
                             concat, union, join, star)

class DerivationTests(LexingtonTestCase):
    """
    These tests check whether the different types of regexes derive correctly.
    """
    def test_epsilon(self):
        assert Epsilon.accepts_empty_string
        self.assert_is(Epsilon.derive("a"), Null)

    def test_null(self):
        assert not Null.accepts_empty_string
        self.assert_is(Null.derive("a"), Null)

    def test_any(self):
        assert not Any.accepts_empty_string
        self.assert_is(Any.derive("a"), Epsilon)
        self.assert_is(Any.derive("b"), Epsilon)

    def test_symbol(self):
        s = Regex("a")
        assert not s.accepts_empty_string
        self.assert_is(s.derive("a"), Epsilon)
        self.assert_is(s.derive("b"), Null)

    def test_string(self):
        s = Regex("abc")
        assert not s.accepts_empty_string
        self.assert_equal(s.derive("a"), Regex("bc"))
        self.assert_equal(s.derive("a").derive("b"), Regex("c"))
        self.assert_is(s.derive("a").derive("b").derive("c"), Epsilon)
        self.assert_is(s.derive("b"), Null)

    def test_union(self):
        s = union(Regex("a"), Regex("b"))
        assert not s.accepts_empty_string
        self.assert_is(s.derive("a"), Epsilon)
        self.assert_is(s.derive("b"), Epsilon)
        self.assert_is(s.derive("c"), Null)

    def test_concat(self):
        s = concat(Regex("a"), Regex("b"))
        assert not s.accepts_empty_string
        b = s.derive("a")
        assert not b.accepts_empty_string
        self.assert_is(b.derive("b"), Epsilon)


class IdentityTests(LexingtonTestCase):
    """
    These tests check that various mathematical identities hold.
    """
    def test_epsilon_concat(self):
        a = Regex("a")
        self.assert_is(concat(a, Epsilon), a)
        self.assert_is(concat(Epsilon, a), a)

    def test_null_concat(self):
        a = Regex("a")
        self.assert_is(concat(a, Null), Null)
        self.assert_is(concat(Null, a), Null)

    def test_null_union(self):
        a = Regex("a")
        self.assert_is(union(a, Null), a)

    def test_star_star(self):
        s = star(Regex("a"))
        self.assert_is(star(s), s)

    def test_epsilon_star(self):
        self.assert_is(star(Epsilon), Epsilon)

    def test_null_star(self):
        self.assert_is(star(Null), Epsilon)


class OperatorTests(LexingtonTestCase):
    """
    These tests check convenience methods of `Regex` instances and operator
    overloads.
    """
    def test_plus_concat(self):
        a, b = Regex("a"), Regex("b")
        self.assert_equal(a + b, concat(a, b))

    def test_bar_union(self):
        a, b = Regex("a"), Regex("b")
        self.assert_equal(a | b, union(a, b))

    def test_star_method(self):
        a = Regex("a")
        self.assert_equal(a.star(), star(a))


suite = make_suite(
    DerivationTests,
    IdentityTests,
    OperatorTests
)
