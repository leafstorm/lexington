===================
Regular Expressions
===================
Lexington implements its own regular expression engine in pure Python.
This provides a few important advantages over using the `re` module:

* Input data can be matched against regexes incrementally.
* Complex regular expressions can be built out of smaller ones.
* The matching algorithm is simpler to understand.


Regular Expression API
======================
.. currentmodule:: lexington.regex

.. autoclass:: Regex
   
   .. automethod:: derive

   .. autoattribute:: accepts_empty_string

   .. rubric:: Methods for Composing Regexes

   .. method:: regex + other

      Creates a regular expression that matches this regex followed by
      `other`. (Equivalent to `concat`.)

   .. method:: regex | other

      Creates a regular expression that either matches this regex or `other`.
      (Equivalent to `union`.)

   .. automethod:: star

   .. automethod:: plus

   .. automethod:: maybe


Special Regexes
---------------
.. autodata:: Null

.. autodata:: Epsilon

.. autodata:: Any


Constructor Functions
---------------------
.. autofunction:: regexify

.. autofunction:: union

.. autofunction:: concat

.. autofunction:: join

.. autofunction:: star


Mathematical Concepts
=====================
The ideas behind "regular expressions" as used in modern programming languages
come from formal language theory (i.e. math). You don't need to read this
section to use Lexington, but it's useful for understanding how Lexington
works and why its regular expressions are constructed a certain way.


Strings and Alphabets
---------------------
The mathematical concept of a string is very similar to how programmers
view it: a sequence of zero or more (but not infinity) symbols from
an alphabet. "Alphabet" doesn't refer to actual alphabets (like the Latin
alphabet or Georgian alphabet), but to any finite set containing symbols.
("Playing card suits," for example, is a perfectly valid alphabet.)

For example, if we use "Unicode codepoints" as our alphabet, the following
are all strings::

    ""              # empty string - commonly called ε (epsilon)
    "A"
    "hello world"
    "Spam, spam, spam, spam..."
    "Ĉu vi parolas Esperanton?"

The Python `str` type (`unicode` in Python 2) is the type of all strings
over the alphabet of Unicode characters. `bytes` (`str` in Python 2) is the
type of all strings over the alphabet of bytes (the numbers 0 through 255).


Languages
---------
A *language* is simply a set of strings. For example:

* The set of all valid Python integer literals
* The set of all valid Python programs
* The set of all Monty Python skits
* The set of names of Monty Python members
* The set of all palindromes
* The set of every string ever
* The empty set (called "null," which is sometimes written as ∅)

One way to describe a set is by explicitly listing every member.
For example, we could describe the set of names of Monty Python members:

.. math::

   \{
       \mathtt{John\,Cleese}, \mathtt{Eric\,Idle}, \mathtt{Terry\,Gilliam},
       \mathtt{Terry\,Jones}, \mathtt{Graham\,Chapman}, \mathtt{Michael\,Palin}
   \}

In Python, this looks like::

    {"John Cleese", "Eric Idle", "Terry Gilliam", "Terry Jones",
     "Graham Chapman", "Michael Palin"}

However, this only works for finite languages. Some languages (like "all
valid Python programs," or "all palindromes") contain an *infinite* number
of strings, and therefore cannot be enumerated.

So, another way to describe a language is by giving criteria for being
part of the set. In math, this is done using "set builder" notation.
An expression for the set of all palindromes would look like:

.. math:: \{ w \mid w = w^\mathcal{R} \}

Which is read as, "All strings :math:`w` where :math:`w` is equal to :math:`w`
reversed." It's similar in concept to Python's set comprehensions::

    {w for w in every_string_ever if w == w[::-1]}

Except that set comprehensions only work when you actually have a finite
number of strings. (Otherwise, Python runs out of memory and crashes.)


Regular Expressions
-------------------
Regular expressions are another way to describe languages, which are similar
to mathematical expressions. For example, here's a regular expression for
"the set of all Python integer literals in base 10:"

.. math::

    (\mathtt{-} \cup \epsilon) \,
    ((\mathtt{1} \cup \cdots \cup \mathtt{9})\,
         (\mathtt{0} \cup \mathtt{1} \cup \cdots \cup \mathtt{9})^*
    \cup \mathtt{0} \mathtt{0}^*)

The basic elements of a regular expression are:

*   :math:`a`, where :math:`a` is any symbol in the alphabet
*   :math:`\epsilon`
*   :math:`\emptyset`

The notation :math:`L(R)` means, "the set of strings described by :math:`R`."
The languages of these basic regular expressions are.

*   :math:`L(a)` is :math:`\{a\}`:
    just the one-symbol string ``"a"``.
*   :math:`L(\epsilon)` is :math:`\{\epsilon\}`:
    just the empty string.
*   :math:`L(\emptyset)` is :math:`\emptyset`:
    no strings at all are in this set.

Then, there are three operations that allow us to build more complicated
regular expressions:

*   :math:`R_1 \circ R_2` (or just :math:`R_1 R_2`) is **concatenation**:
    first, a string in :math:`R_1`, then a string in :math:`R_2`.
*   :math:`R_1 \cup R_2` is **union**:
    any string either in :math:`R_1` or :math:`R_2`.
*   :math:`R_1^*` is **Kleene star**:
    zero or more strings in :math:`R_1` repeated.

Here are some examples:

*   :math:`\mathtt{abc}` describes ``"abc"``
*   :math:`\mathtt{a} \cup \mathtt{b}` describes ``"a"`` and ``"b"``
*   :math:`\mathtt{a} \cup \epsilon` describes ``"a"`` and ``""``
*   :math:`\mathtt{a}^*` describes ``""``, ``"a"``, ``"aa"``, and so on
*   :math:`\mathtt{aa}^*` describes ``"a"``, ``"aa"``, ``"aaa"``, and so on
*   :math:`(\mathtt{a} \cup \mathtt{b})^*` describes
    ``""``, ``"a"``, ``"b"``, ``"aa"``, ``"ab"``, ``"ba"``, ``"aaa"``, etc.

Going back to our integer-literal regular expression above, we can read it
as:

    "First, there will either be a ``-``, or nothing.
    Then, we either have a digit from ``1``-``9`` followed by any number of
    digits from ``0``-``9``, or one or more ``0``'s."

So, regular expressions are useful for answering both "what strings are
in this language?" and "how do I tell if a string is in this language?".


Unix's Regular Expressions
--------------------------
Here's how to translate traditional Unix regular expressions (as implemented
in Python's `re` module) to their mathematical counterparts:

*   ``R*`` is exactly the same as :math:`R^*`.
*   ``R+`` is equivalent to :math:`R\,R^*`.
*   ``R?`` is equivalent to :math:`R \cup \epsilon`.
*   ``R{m}`` is equivalent to :math:`R R \cdots R`, however many times.
*   ``R{m,n}`` is really complicated in math notation, but trust me, it works.
*   ``R|S`` is equivalent to :math:`R \cup S`.
*   ``[abc]`` is equivalent to :math:`\mathtt{a} \cup \mathtt{b}
    \cup \mathtt{c}`. (Ranges like ``a-z`` would add a union term for each
    character in the range.)
*   ``\d`` and friends are shortcuts for ``[]`` set notation, so they
    would be translated the same way.

Some features of Python's regular expression module aren't present in the
mathematical model.


A Side Note: Non-Regular Languages
----------------------------------
Regular expressions are called regular expressions because they are only
capable of matching regular languages. One language they are *not* capable
of matching is the bracket language, which just looks like this::

    ""
    "[]"
    "[[]]"
    "[[[]]]"

The bracket language is not a regular language -- it is a context-free
language. Therefore, no matter how hard you try, you can never create a
regular expression that can correctly recognize whether a string is in the
bracket language or not.

If you take a course or read a book about automata, you'll learn
exactly what qualifies a language as regular, context-free, or
context-sensitive. Sometimes it's obvious, but other times, you need to use
a mathematical proof to determine what class a language falls into.

However, in general you can assume that any *recursive* language is not
regular. The bracket language is recursive: each bracket pair may contain
another bracket pair inside it, and there's no limit to how deep the
brackets can be nested. Python is also recursive, because statements like
for loops can contain other statements, and expressions can contain other
expressions. HTML is recursive, because each tag can contain other tags
inside. (Which explains `this famous Stack Overflow answer`_.)

.. _this famous Stack Overflow answer: http://stackoverflow.com/a/1732454/244407


Derivatives of Languages
------------------------
There are many strategies for actually parsing things with regular
expressions, including NFA conversion, DFA conversion, and backtracking.
The one Lexington uses is arguably the simplest, and it's based on the idea
of the derivative of a language.

The derivative in language theory isn't really related to the derivative in
calculus. The derivative of a language with respect to a character
is defined as "all the strings in a language that begin with that character,
without that character at the beginning." Mathematically, it's:

.. math::

    D_c(L) = \{ w \mid c w \in L \}

And a Python implementation for finite languages would look like::

    def derivative(language, char):
        return {s[1:] for s in language if s[0] == char}

To see how this is useful for pattern matching, consider this language, which
consists of all Triangle Transit routes in Chapel Hill::

    >>> routes = {"400", "405", "420", "800", "805", "CRX"}

Let's say we want to test whether ``"405"`` is in this language.

    >>> derivative(routes, "4")
    {"00", "05", "20"}
    >>> derivative(_, "0")
    {"0", "5"}
    >>> derivative(_, "5")
    {""}

We repeatedly derive the language with each character in the input string.
After deriving all the characters, if ``""`` (the empty string) is in the
result set, we accept. Here's an example of an unsuccessful match, this
time for ``"CAT"``::

    >>> derivative(routes, "C")
    {"RX"}
    >>> derivative(routes, "A")
    set()

If we ever reach the empty set while deriving, that means the string is
definitely not in the language.

However, compared to ``"405" in routes``, this is really inefficient.
It's also impossible to actually compute this when we have an infinite set
(like "Python integer literals").


Derivatives of Regular Expressions
----------------------------------
However, the derivative is also defined on regular expressions -- and if we
have a regular expression that describes a language, then the derivative
of that regular expression describes the derivative of that language.

Also, taking the derivative of a regular expression is really simple
(don't be fooled by the giant tower of math):

.. math::

    & D_c(\emptyset)        &=  \emptyset \\
    & D_c(\epsilon)         &=  \emptyset \\
    & D_c(c)                &=  \epsilon \\
    & D_c(c')               &=  \emptyset
                                & \quad \text{ if } c \neq c' \\
    & D_c(R_1 \circ R_2)    &=  D_c(R_1) \circ R_2 \cup D_c(R_2)
                                & \quad \text{ if } \epsilon \in R_2 \\
    & D_c(R_1 \circ R_2)    &=  D_c(R_1) \circ R_2
                                & \quad \text{ otherwise} \\
    & D_c(R_1 \cup R_2)     &=  D_c(R_1) \cup D_c(R_2) \\
    & D_c(R^*)              &=  D_c(R) \circ R^*

This means that we can use the derivative matching algorithm above on
regular expressions directly -- and besides being easy to implement, it's
actually pretty efficient. And this is how Lexington's regexes work.
