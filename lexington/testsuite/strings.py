# -*- coding: utf-8 -*-
"""
lexington.testsuite.strings
===========================
This file contains API-level tests for the string support module.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
from __future__ import unicode_literals
import unittest
from . import LexingtonTestCase, make_suite

from lexington.strings import (Text, Codepoint, Bytestring, Byte,
                               Strings, Characters, string_type,
                               PYTHON_3000, n, native_strings)


class TypeTests(LexingtonTestCase):
    """
    This tests the definitions of the string types.
    """
    def test_text(self):
        text = "Spam!"
        self.assert_instance(text, Text)
        self.assert_instance(text[0], Codepoint)
        self.assert_instance(text, Strings)
        self.assert_instance(text[0], Characters)

    def test_binary(self):
        bytestring = b"Spam!"
        self.assert_instance(bytestring, Bytestring)
        self.assert_instance(bytestring[0], Byte)
        self.assert_instance(bytestring, Strings)
        self.assert_instance(bytestring[0], Characters)

    def test_string_type_text(self):
        self.assert_is(string_type("Spam!"), Text)
        self.assert_is(string_type("Spam!"[0]), Text)

    def test_string_type_binary(self):
        self.assert_is(string_type(b"Spam!"), Bytestring)
        self.assert_is(string_type(b"Spam!"[0]), Bytestring)

    def test_string_type_others(self):
        self.assert_raises(TypeError, string_type, Ellipsis)

    def test_native(self):
        message = "ĉapelo"
        if PYTHON_3000:
            self.assert_is(n(message), message)
        else:
            self.assert_equal(n(message), message.encode("utf8"))

    def test_native_strings(self):
        message = "ĉapelo"
        ident = native_strings(lambda s: s)
        self.assert_is(ident(Ellipsis), Ellipsis)
        if PYTHON_3000:
            self.assert_is(ident(message), message)
        else:
            self.assert_equal(ident(message), message.encode("utf8"))


suite = make_suite(
    TypeTests
)
