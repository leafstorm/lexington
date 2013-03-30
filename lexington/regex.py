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
from __future__ import unicode_literals
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import Sequence
from .strings import Strings, Characters, native_strings, n, string_type


### Very scary metaprogramming ###

class _RegexClass(ABCMeta):
    """
    This is a metaclass, and a giant hack. It has two primary functions:

    First, it obviates the needs to decorate every `__repr__` method with
    `~lexington.strings.native_strings`.

    Second, because it doesn't make sense to instantiate `Regex` directly,
    it's convenient to use it as a factory for actual `Regex` subclasses.
    However, the behavior of `__new__` can be a bit confusing.
    By overriding `__call__` in the metaclass directly, we can prevent the
    whole "`__new__`/`__init__`" stack from entering the picture when using
    `Regex` as a factory function.
    """
    def __new__(mcls, name, bases, namespace):
        # __new__ is called on the metaclass when creating a class.
        # It has the chance to modify the class's namespace before the
        # class is actually created.
        # We use this as a chance to wrap the __repr__ method.
        if '__repr__' in namespace:
            namespace['__repr__'] = native_strings(namespace['__repr__'])
        return super(_RegexClass, mcls).__new__(mcls, name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        # A class is just an object, and a metaclass is the type of that
        # object. So, when you do AClass(...), it calls the __call__ method
        # on that class, just like any other object.
        if cls is Regex:
            return regexify(*args, **kwargs)
        else:
            return super(_RegexClass, cls).__call__(*args, **kwargs)


_Regex = _RegexClass(n("_Regex"), (object,), dict(
    __doc__ = "This is needed for Python 3 compatibility. "
              "The metaclass syntax changed between Python 3 and Python 2, "
              "so we need to construct a base class programmatically.",
    __slots__ = ()
))


### Actual regular expression classes ###


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
    def accepts_empty_string(self):
        """
        Indicates whether this regular expression will accept the empty
        string.
        """
        pass

    @abstractproperty
    def alphabet(self):
        """
        Indicates the alphabet of the strings this regular expression can
        match. `None` indicates that this regular expression is
        independent of alphabet.

        The alphabet will usually be `~lexington.strings.Text` or
        `~lexington.strings.Bytestring`.
        """
        pass

    def __eq__(self, other):
        return type(self) is type(other) and hash(self) == hash(other)

    @abstractmethod
    def __hash__(self):
        pass

    ### High-level regex operations

    def match(self, subject):
        """
        Determines whether the `subject` matches this regex. This performs a
        total match -- if you want the behavior of `re.match`, which only
        matches a prefix, use `match_prefix`.

        This returns `True` if the match succeeds, and `False` if not.

        :param subject: The string to match against this regex.
        """
        re = self
        for sym in subject:
            re = re.derive(sym)
            if re is Null:
                return False
        return re.accepts_empty_string

    @property
    def literal(self):
        """
        If this regular expression matches a literal string exactly, this
        property contains that string. Otherwise, it will be `None`.
        (You can generally only assume that regexes constructed *from* literal
        strings will have this property.)
        """
        return None

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

    def __pow__(self, count):
        return repeat(self, count)


class EpsilonRegex(Regex):
    """
    A regular expression that matches the empty string.
    """
    __slots__ = ()

    def derive(self, sym):
        return Null

    accepts_empty_string = True

    alphabet = None

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

    alphabet = None

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

    @property
    def alphabet(self):
        return string_type(self.sym)

    @property
    def literal(self):
        return self.sym

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

    alphabet = None

    def __repr__(self):
        return "Any"

    def __hash__(self):
        return hash(type(self))


class UnionRegex(Regex):
    """
    A regular expression that will match any of multiple options.

    :param options: The regular expressions to accept.
    """
    __slots__ = ('options', 'alphabet')

    def __init__(self, options):
        self.alphabet = None
        self.options = frozenset(options)
        for opt in self.options:
            if opt.alphabet is not None:
                if self.alphabet is None:
                    self.alphabet = opt.alphabet
                elif opt.alphabet is not self.alphabet:
                    raise TypeError(n("Cannot mix alphabets %r and %r in "
                                      "union" %
                                      (self.alphabet, opt.alphabet)))

    def derive(self, sym):
        return union(*(r.derive(sym) for r in self.options))

    @property
    def accepts_empty_string(self):
        return any(r.accepts_empty_string for r in self.options)

    def __repr__(self):
        return " | ".join(repr(r) for r in self.options)

    def __hash__(self):
        return hash((id(type(self)), self.options))


class ConcatRegex(Regex):
    """
    A regular expression that matches two regular expressions in a row.
    """
    __slots__ = ('prefix', 'suffix', 'alphabet')

    def __init__(self, prefix, suffix):
        self.prefix = prefix
        self.suffix = suffix

        # This logic is admittedly a bit twisty. The idea is:
        # If the prefix and suffix are alphabet-independent, so is this.
        # If the prefix and suffix have the same alphabet, or one has an
        # alphabet and the other doesn't, this will have the same alphabet.
        # If the prefix and suffix have different alphabets, that's an error.
        alpha_pre = prefix.alphabet
        alpha_suf = suffix.alphabet
        if alpha_pre is not None or alpha_suf is not None:
            if alpha_pre is not alpha_suf:
                raise TypeError(n("Cannot concatenate alphabets %r and %r" %
                                  (alpha_pre, alpha_suf)))
            self.alphabet = alpha_pre if alpha_suf is None else alpha_suf
        else:
            self.alphabet = None

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

    @property
    def literal(self):
        if self.prefix.literal and self.suffix.literal:
            return self.prefix.literal + self.suffix.literal
        else:
            return None

    def __repr__(self):
        if self.literal:
            return "Regex(%r)" % self.literal
        else:
            return "%r + %r" % (self.prefix, self.suffix)

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

    @property
    def alphabet(self):
        return self.regex.alphabet

    def __repr__(self):
        return "star(%r)" % self.regex

    def __hash__(self):
        return hash((id(type(self)), self.regex))


class RepeatRegex(Regex):
    """
    A regular expression that will match a certain regex, repeated a specific
    number of times.

    :param regex: The regular expression describing the strings to repeat.
    :param count: The number of times to repeat it.
    """
    __slots__ = ('regex', 'count')

    def __init__(self, regex, count):
        if count < 2:
            raise ValueError("Repeat must be greater than 1" % count)
        self.regex = regex
        self.count = count

    def derive(self, sym):
        return concat(self.regex.derive(sym),
                      repeat(self.regex, self.count - 1))

    accepts_empty_string = False

    @property
    def alphabet(self):
        return self.regex.alphabet

    def __repr__(self):
        return "%r ** %d" % (self.regex, self.count)

    def __hash__(self):
        return hash((id(type(self)), self.regex, self.count))


### Regex constructors ###


def regexify(e):
    """
    Converts a Python object to a `Regex`. If it's already a `Regex`, it just
    returns it. It will also accept any string or character type, and create
    a regex that matches that exactly.

    :param e: The Python object to create a regex of.
    """
    if isinstance(e, Regex):
        return e
    elif isinstance(e, Strings):
        if len(e) == 0:
            return Epsilon
        return join(SymbolRegex(sym) for sym in e)
    elif isinstance(e, Characters):
        return SymbolRegex(e)
    else:
        raise TypeError(n("Instances of %r can't be automatically converted "
                          "to regular expressions" % type(e)))


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


def repeat(regex, count):
    """
    Creates a regular expression that accepts `regex` repeated a specific
    number of times.

    :param regex: The regular expression describing the strings to reepeat.
    :param count: The number of times to repeat it.
    """
    if count == 0:
        return Epsilon
    elif count == 1:
        return regex
    elif regex is Epsilon:
        return Epsilon
    elif regex is Null:
        return Null
    else:
        return RepeatRegex(regexify(regex), count)
