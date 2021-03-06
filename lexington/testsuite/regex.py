# -*- coding: utf-8 -*-
"""
lexington.testsuite.regex
=========================
This file contains API-level tests for the regular expression module.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
from __future__ import unicode_literals
import unittest
from . import LexingtonTestCase, make_suite

from lexington.regex import (Regex, Null, Epsilon, Any,
                             concat, union, join, star, repeat)
from lexington.strings import Text, Bytestring

class MatchingTests(LexingtonTestCase):
    """
    These tests check regular expressions matching strings.
    """
    def test_epsilon(self):
        self.assert_(Epsilon.match(""))
        self.assert_false(Epsilon.match("abc"))

    def test_not_null(self):
        self.assert_false(Null.match(""))
        self.assert_false(Null.match("abc"))

    def test_simple(self):
        self.assert_(Regex("abc").match("abc"))
        self.assert_false(Regex("abc").match("ab"))
        self.assert_false(Regex("abc").match("abcd"))

    def test_union(self):
        msv = Regex("spam") | Regex("eggs")
        self.assert_(msv.match("spam"))
        self.assert_(msv.match("eggs"))
        self.assert_false(msv.match("ham"))

    def test_complex(self):
        msv = Regex("spam") | Regex("eggs")
        total = msv + (" " + msv).star()
        self.assert_(total.match("spam"))
        self.assert_(total.match("spam spam spam spam"))
        self.assert_(total.match("eggs spam eggs"))
        self.assert_false(total.match("eggs spam "))
        self.assert_false(total.match(" "))
        self.assert_false(total.match("spam spam ham eggs"))


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

    def test_repeat(self):
        s3 = repeat(Regex("a"), 3)
        assert not s3.accepts_empty_string
        s2 = s3.derive("a")
        self.assert_equal(s2, repeat(Regex("a"), 2))
        s1 = s2.derive("a")
        self.assert_equal(s1, Regex("a"))
        self.assert_is(s1.derive("a"), Epsilon)

        self.assert_is(s3.derive("b"), Null)


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

    def test_repeat_0_1(self):
        a = Regex("a")
        self.assert_is(repeat(a, 0), Epsilon)
        self.assert_is(repeat(a, 1), a)

    def test_epsilon_repeat(self):
        self.assert_is(repeat(Epsilon, 5), Epsilon)

    def test_null_repeat(self):
        self.assert_is(repeat(Null, 5), Null)


class AlphabetTests(LexingtonTestCase):
    """
    These tests check that regexes report the alphabet they match correctly.
    """
    def test_alphabet_independents(self):
        self.assert_is(Epsilon.alphabet, None)
        self.assert_is(Null.alphabet, None)
        # TODO: Add tests for Any once we decide how to handle that

    def test_alphabets_of_strings(self):
        text = Regex("GET")
        ascii = Regex(b"GET")
        self.assert_is(text.alphabet, Text)
        self.assert_is(ascii.alphabet, Bytestring)

    def test_alphabets_of_symbols(self):
        text = "GET"
        ascii = b"GET"
        self.assert_is(Regex(text[0]).alphabet, Text)
        self.assert_is(Regex(ascii[0]).alphabet, Bytestring)

    def test_non_strings(self):
        self.assert_raises(TypeError, Regex, Ellipsis)

    def test_concatenation(self):
        terry = "Terry"
        gilliam = "Gilliam"
        pratchett = b"Pratchett"

        self.assert_is(concat(terry, gilliam).alphabet, Text)
        self.assert_raises(TypeError, concat, terry, pratchett)

    def test_union(self):
        terry = "Terry"
        michael = "Michael"
        ringo = b"Ringo"

        self.assert_is(union(terry, michael).alphabet, Text)
        self.assert_is(union(terry, Epsilon).alphabet, Text)
        self.assert_raises(TypeError, concat, terry, michael, ringo)

    def test_star(self):
        self.assert_is(star("Terry").alphabet, Text)

    def test_repeat(self):
        self.assert_is(repeat("Terry", 5).alphabet, Text)


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

    def test_pow_repeat(self):
        a = Regex("a")
        self.assert_equal(a ** 3, repeat(a, 3))

    def test_star_method(self):
        a = Regex("a")
        self.assert_equal(a.star(), star(a))


suite = make_suite(
    MatchingTests,
    DerivationTests,
    IdentityTests,
    AlphabetTests,
    OperatorTests
)
