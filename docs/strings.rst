===========================
Cross-Python String Support
===========================
.. currentmodule:: lexington.strings

Lexington is designed to support Python 2.6, 2.7, 3.2, 3.3, and any future
versions of Python 3, using the same codebase. (It's still too early to
make any judgements about Python 4.)

Because Lexington deals heavily with text and bytes, its strategy is to use::

    from __future__ import unicode_literals

This can cause problems on Python 2, in situations where the interpreter
internals expect binary data, and turn `unicode` into ASCII (or just explode
on it). However, it ensures that our strings have consistent semantics
across Python versions.

.. data:: PYTHON_3000

   This constant is `True` if we are running on Python 3, `False` if we are
   running on Python 2.


Analyzing String Types
======================
.. data:: Text

   The type used for Unicode text data on the current platform.

.. data:: Codepoint

   The type used for individual Unicode code points on the current platform
   (that is, what you get when you iterate over `Text`).

.. data:: Bytestring

   The type used for binary data on the current platform.

.. data:: Byte

   The type used for individual bytes on the current platform
   (that is, what you get when you iterate over `Bytestring`).

.. data:: Strings

   A tuple of the types that indicate strings.

.. data:: Characters

   A tuple of the types that indicate characters
   (that is, anything you can get iterating over a class in `Strings`).

.. autofunction:: string_type


String Helpers
==============
.. warning::

   These are intended primarily for internal use, and as such are subject
   to change more frequently than the rest of Lexington's API.
   Also, these are designed for code that uses ``from __future__ import
   unicode_literals``.

.. autofunction:: n

.. autofunction:: native_strings
