# -*- coding: utf-8 -*-
"""
lexington.testsuite
===================
This package contains Lexington's unit tests. Most modules in the `lexington`
package have two testsuites -- one labeled `impl`, one not. The `impl` version
checks the tests' internals, the other only uses the documented API.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
from __future__ import unicode_literals
import unittest

class LexingtonTestCase(unittest.TestCase):
    """
    An extension of the standard `unittest.TestCase`, so that the method
    names don't look like we're writing Java.
    """
    def setup(self):
        pass

    def teardown(self):
        pass

    def setUp(self):
        self.setup()

    def tearDown(self):
        self.teardown()

    def assert_true(self, e):
        return self.assertTrue(e)

    def assert_false(self, e):
        return self.assertFalse(e)

    def assert_is(self, a, b):
        if hasattr(self, 'assertIs'):
            return self.assertIs(a, b)
        else:
            return self.assert_(a is b, "%r is not %r" % (a, b))

    def assert_instance(self, instance, cls):
        if hasattr(self, 'assertIsInstance'):
            return self.assertIsInstance(instance, cls)
        else:
            return self.assert_(isinstance(instance, cls),
                                "%r is not an instance of %r" %
                                (instance, cls))

    def assert_equal(self, a, b):
        return self.assertEqual(a, b)

    def assert_raises(self, *args, **kwargs):
        return self.assertRaises(*args, **kwargs)


def make_suite(*cases):
    def suite():
        test_suite = unittest.TestSuite()

        for case in cases:
            test_suite.addTest(unittest.makeSuite(case))

        return test_suite
    return suite


def suite():
    from . import strings, regex, regex_impl

    test_suite = unittest.TestSuite()

    test_suite.addTest(strings.suite())
    test_suite.addTest(regex.suite())
    #test_suite.addTest(regex_impl.suite())

    return test_suite
