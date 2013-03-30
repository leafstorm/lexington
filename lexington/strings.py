# -*- coding: utf-8 -*-
"""
lexington.strings
=================
This module provides utilities for cross-Python string handling. Lexington's
strategy is to use ``from __future__ import unicode_literals`` internally,
to ensure that all of our string literals have consistent semantics.
The string helpers here are designed with this in mind.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
from __future__ import unicode_literals
import sys
from functools import wraps

#: This constant is `True` if we are running on Python 3, `False` if we are
#: running on Python 2. (Note that only Python 2.6, 2.7, 3.2, and 3.3 are
#: supported.)
PYTHON_3000 = sys.version_info[0] == 3


#: The type used for Unicode text data on the current platform.
Text = str if PYTHON_3000 else unicode

#: The type used for individual Unicode code points on the current platform
#: (that is, what you get when you iterate over `Text`).
Codepoint = Text


#: The type used for binary data on the current platform.
Bytestring = bytes if PYTHON_3000 else str

#: The type used for individual bytes on the current platform
#: (that is, what you get when you iterate over `Bytestring`).
Byte = int if PYTHON_3000 else str


#: A tuple of the types that indicate strings.
Strings = (Text, Bytestring)

#: A tuple of the types that indicate characters
#: (that is, anything you can get iterating over a class in `Strings`).
Characters = (Codepoint, Byte)


if PYTHON_3000:
    def n(string):
        """
        Ensures that a Unicode string is in the current Python's "native
        format" -- the format the interpreter expects strings to be in.
        On Python 3, this is Unicode. On Python 2, this is a UTF-8 encoded
        bytestring.

        (You probably shouldn't be using this in performance-critical code.
        It should only be used for environments like `__repr__` or exception
        messages where Python 2's behavior of encoding to ASCII can cause
        problems, and its use is conditional.)

        :param string: A Unicode string that needs to pass through the
                       interpreter internals.
        """
        return string
else:
    def n(string):
        """
        Ensures that a Unicode string is in the current Python's "native
        format" -- the format the interpreter expects strings to be in.
        On Python 3, this is Unicode. On Python 2, this is a UTF-8 encoded
        bytestring.

        (This function is only intended for code paths where Python 2's
        default behavior of encoding as ASCII could potentially cause
        problems. If the string is guaranteed to be ASCII, and isn't
        passing through a code path that will *only* work with `str`,
        you don't need this.)

        :param string: A Unicode string that needs to pass through the
                       interpreter internals.
        """
        return string.encode("utf-8")


def native_strings(fn):
    """
    A decorator for functions that need to return a "native string"
    (see `n`). Note that on Python 2, it will only encode the result
    when the function's return value is actually a string.
    """
    if PYTHON_3000:
        return fn
    else:
        @wraps(fn)
        def native_string_function(*args, **kwargs):
            s = fn(*args, **kwargs)
            return s.encode("utf-8") if isinstance(s, Text) else s
        return native_string_function


def string_type(string):
    """
    Returns the Python type of a string with `string` as a symbol or
    substring. (This can't just use `type`, because it has to take into
    account that on Python 3, the "symbols" for a bytestring are `int`.)

    :param string: A string or symbol.
    :raises TypeError: If a non-string, non-symbol character is provided.
    """
    if isinstance(string, Text):
        return Text
    elif isinstance(string, (Bytestring, Byte)):
        return Bytestring
    else:
        raise TypeError(n("%r is not a string type" % type(string)))
