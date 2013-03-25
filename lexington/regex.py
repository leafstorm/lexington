"""
lexington.regex
===============
Lexington's lexers operate using the derivative of a regular expression.
Python's regular expressions as implemented in the `re` module are not
actually regular expressions, and probably wouldn't give you access to their
derivatives even if they were. So, this implementation is necessary.

:copyright: (C) 2013, Matthew Frazier
:license:   Released under the MIT/X11 license, see LICENSE for details
"""
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import Sequence


### Actual regular-expression classes ###

class _RegexClass(ABCMeta):
    """
    We can't instantiate `Regex` directly anyway, since it's an ABC, so
    it's intuitive to just use ``Regex(string)``. However, some weird
    stuff happened when I tried to use `__new__`. Therefore, I overrode
    `__call__` in the metaclass instead.

    This is a horrible hack. However, it does illuminate the nature of
    classes and metaclasses.
    """
    def __call__(self, *args, **kwargs):
        if self is Regex:
            return regexify(*args, **kwargs)
        else:
            return super(_RegexClass, self).__call__(*args, **kwargs)


_Regex = _RegexClass("_Regex", (object,), {
    __doc__: "This is needed for Python 3 compatibility."
})


class Regex(_Regex):
    """
    This is the abstract base class for elements of regular expressions.
    (It's also used as a factory for converting mundane Python data types
    like strings into regular expressions.)

    `Regex` objects are immutable, hashable, and comparable.

    In practice, `Regex`'s subclasses should be regarded as implementation
    details. You shouldn't attempt to create instances of them, create new
    subclasses of `Regex`, or test that a regex is an instance of a
    particular `Regex` subclass.

    :param e: An expression to convert into a regular expression.
              (This is equivalent to `regexify`.)
    """
    __metaclass__ = _RegexClass
    __slots__ = ()

    ### Abstractions to override

    @abstractmethod
    def derive(self, sym):
        """
        Returns the derivative of this regular expression with respect to
        a symbol. You can view it as::

            {s[1:] for s in languages_generated_by(self) if s and s[0] == sym}

        :param sym: The symbol to derive this regular expression with regards
                    to.
        """
        pass

    @abstractproperty
    def accepts_empty_string():
        """
        Indicates whether this regular expression will accept the empty
        string.
        """
        pass

    def __eq__(self, other):
        return type(self) is type(other) and hash(self) == hash(other)

    @abstractmethod
    def __hash__(self):
        pass

    ### Operator overloads and convenience methods

    def star(self):
        """
        Creates a regular expression that accepts this one repeated any
        number of times. (Equivalent to the `~lexington.regex.star` function.)
        """
        return star(self)

    def plus(self):
        """
        Creates a regular expression that accepts this one repeated any
        number of times.
        """
        return concat(self, star(self))

    def maybe(self):
        """
        Creates a regular expression that accepts this one, or the empty
        string.
        """
        return union(self, Epsilon)

    def __add__(self, suffix):
        return concat(self, suffix)

    def __radd__(self, prefix):
        return concat(prefix, self)

    def __or__(self, other):
        return union(self, other)

    def __ror__(self, other):
        return union(other, self)


class EpsilonRegex(Regex):
    """
    A regular expression that matches the empty string.
    """
    __slots__ = ()

    def derive(self, sym):
        return Null

    accepts_empty_string = True

    def __repr__(self):
        return "Epsilon"

    def __hash__(self):
        return hash(type(self))


class NullRegex(Regex):
    """
    A regular expression that doesn't match any strings, even the empty
    string.
    """
    __slots__ = ()

    def derive(self, sym):
        return self

    accepts_empty_string = False

    def __repr__(self):
        return "Null"

    def __hash__(self):
        return hash(type(self))


class SymbolRegex(Regex):
    """
    A regular expression that matches a particular symbol.

    :param sym: The symbol to match.
    """
    __slots__ = ('sym')

    def __init__(self, sym):
        self.sym = sym

    def derive(self, sym):
        return Epsilon if sym == self.sym else Null

    accepts_empty_string = False

    def __repr__(self):
        return "Regex(%r)" % self.sym

    def __hash__(self):
        return hash((id(type(self)), self.sym))


class AnySymbolRegex(Regex):
    """
    A regular expression that matches ANY symbol (but not the lack of one).
    Equivalent to ``.`` in Python's regex notation.

    :param sym: The symbol to match.
    """
    __slots__ = ()

    def derive(self, sym):
        return Epsilon

    accepts_empty_string = False

    def __repr__(self):
        return "Any"

    def __hash__(self):
        return hash(type(self))


class UnionRegex(Regex):
    """
    A regular expression that will match any of multiple options.

    :param options: The regular expressions to accept.
    """
    __slots__ = ('options')

    def __init__(self, options):
        self.options = frozenset(options)

    def derive(self, sym):
        return union(*(r.derive(sym) for r in self.options))

    @property
    def accepts_empty_string(self):
        return any(r.accepts_empty_string for r in self.options)

    def __repr__(self):
        return "union(%s)" % ", ".join(repr(r) for r in self.options)

    def __hash__(self):
        return hash((id(type(self)), self.options))


class ConcatRegex(Regex):
    """
    A regular expression that matches two regular expressions in a row.
    """
    __slots__ = ('prefix', 'suffix')

    def __init__(self, prefix, suffix):
        self.prefix = prefix
        self.suffix = suffix

    def derive(self, sym):
        if self.prefix.accepts_empty_string:
            return union(concat(self.prefix.derive(sym), self.suffix),
                         self.suffix.derive(sym))
        else:
            return concat(self.prefix.derive(sym), self.suffix)

    @property
    def accepts_empty_string(self):
        return (self.prefix.accepts_empty_string and
                self.suffix.accepts_empty_string)

    def __repr__(self):
        return "concat(%r, %r)" % (self.prefix, self.suffix)

    def __hash__(self):
        return hash((id(type(self)), self.prefix, self.suffix))


class StarRegex(Regex):
    """
    A regular expression that will match a certain regex, repeated any number
    of times.

    :param regex: The regular expression describing the strings to repeat.
    """
    __slots__ = ('regex')

    def __init__(self, regex):
        self.regex = regex

    def derive(self, sym):
        return concat(self.regex.derive(sym), self)

    accepts_empty_string = True

    def __repr__(self):
        return "star(%r)" % self.regex

    def __hash__(self):
        return hash((id(type(self)), self.regex))


### Regex Constructors

def regexify(e):
    """
    Converts a Python object to a `Regex`. If it's already a `Regex`, it just
    returns it. If it's an iterable, it will treat each element as a symbol,
    and return their concatenation. (So this will work for `str`, `unicode`,
    lists, etc.) Otherwise, it just treats it as a symbol.

    :param e: The Python object to create a regex of.
    """
    if isinstance(e, Regex):
        return e
    elif hasattr(e, '__iter__') or isinstance(e, basestring):
        if hasattr(e, '__len__') and len(e) == 0:
            return Epsilon
        return join(SymbolRegex(sym) for sym in e)
    else:
        return SymbolRegex(e)


#: A regular expression that matches any single symbol.
Any = AnySymbolRegex()

#: A regular expression that matches the empty string.
Epsilon = EpsilonRegex()

#: A regular expression that refuses to accept *anything* -- even the
#: empty string.
Null = NullRegex()


def union(*options):
    """
    Creates a regular expression that accepts *any* of the following regexes.

    :param options: The regular expressions to accept.
    """
    # A list comprehension would be cleaner, but we need to be able to check
    # the value *after* processing to leave out Nulls.
    s = set()
    for regex in options:
        if isinstance(regex, UnionRegex):
            s.update(regex.options)
        else:
            regex = regexify(regex)
            if regex is not Null:
                s.add(regex)
    if not s:
        return Null
    elif len(s) == 1:
        return s.pop()
    else:
        return UnionRegex(s)


def concat(prefix, suffix):
    """
    Concatenates two regular expressions, such that `prefix` will be matched,
    then `suffix` will be matched after it is complete.

    :param prefix: The first regular expression.
    :param suffix: The second regular expression.
    """
    prefix = regexify(prefix)
    suffix = regexify(suffix)
    if prefix is Null or suffix is Null:
        return Null
    elif prefix is Epsilon:
        return suffix
    elif suffix is Epsilon:
        return prefix
    else:
        return ConcatRegex(prefix, suffix)


def join(regexes):
    """
    Concatenates a sequence of regular expressions, such that each one
    will be matched successively. (Note that a `Null` value anywhere in the
    sequence will result in a `Null` overall.) A zero-length sequence
    will return `Epsilon`.

    :param regexes: The regular expressions to concatenate.
    """
    if not isinstance(regexes, Sequence):
        regexes = tuple(regexes)

    n = len(regexes)
    if n == 2:
        return concat(regexes[0], regexes[1])
    elif n == 1:
        return regexify(regexes[0])
    elif n == 0:
        return Epsilon
    else:
        # This is a right fold (`reduce` backwards).
        # [-2::-1] is slice for "start at the next-to-last and go in reverse."
        final = regexes[-1]
        for regex in regexes[-2::-1]:
            final = concat(regex, final)
            # Break early on Null.
            if final is Null:
                return Null
        return final


def star(regex):
    """
    Creates a regular expression that accepts `regex`, repeated any number
    of times -- even 0.

    :param regex: The regular expression describing the strings to repeat.
    """
    if regex is Epsilon:
        return Epsilon
    elif regex is Null:
        return Epsilon
    elif isinstance(regex, StarRegex):
        # r* == r**, so we can avoid wrapping it again and wasting time.
        return regex
    else:
        return StarRegex(regexify(regex))
