"""
The pscript module provides functionality for transpiling Python code
to JavaScript.

Quick intro
-----------

This is a brief intro for using PScript. For more details see the
sections below.

PScript is a tool to write JavaScript using (a subset) of the Python
language. All relevant builtins, and the methods of list, dict and str
are supported. Not supported are set, slicing with steps, ``yield`` and
imports. Other than that, most Python code should work as expected ...
mostly, see caveats below. If you try hard enough the JavaScript may
shine through. As a rule of thumb, the code should behave as expected
when correct, but error reporting may not be very Pythonic.

The most important functions you need to know about are
:func:`py2js <pscript.py2js>` and
:func:`evalpy <pscript.evalpy>`.
In principal you do not need knowledge of JavaScript to write PScript
code, though it does help in corner cases.


Goals
-----

There is an increase in Python projects that target web technology to
handle visualization and user interaction.
PScript grew out of a desire to allow writing JavaScript callbacks in
Python, to allow user-defined interaction to be flexible, fast, and
stand-alone.

This resulted in the following two main goals:

* To make writing JavaScript easier and less frustrating, by letting
  people write it with the Python syntax and builtins, and fixing some
  of JavaScripts quirks.
* To allow JavaScript snippets to be defined naturally inside a Python
  program.

Code produced by PScript works standalone. Any (PScript-compatible)
Python snippet can be converted to JS; you don't need another JS library
to run it.

PScript can also be used to develop standalone JavaScript (AMD) modules.


PScript is just JavaScript
--------------------------

The purpose of projects like Skulpt or PyJS is to enable full Python
support in the browser. This approach will always be plagued by a
fundamental limitation: libraries that are not pure Python (like numpy)
will not work.

PScript takes a more modest approach; it is a tool that allows one to
write JavaScript with a Python syntax. PScript is just JavaScript.

This means that depending on what you want to achieve, you may still need
to know a thing or two about how JavaScript works. Further, not all Python
code can be converted (e.g. import is not supported), and
lists and dicts are really just JavaScript arrays and objects, respectively.


Pythonic
--------

PScript makes writing JS more "Pythonic". Apart from allowing Python syntax
for loops, classes, etc, all relevant Python builtins are supported,
as well as the methods of list, dict and str. E.g. you can use
``print()``, ``range()``, ``L.append()``, ``D.update()``, etc.

The empty list and dict evaluate to false (whereas in JS it's
true), and ``isinstance()`` just works (whereas JS' ``typeof`` is
broken).

Deep comparisons are supported (e.g. for ``==`` and ``in``), so you can
compare two lists or dicts, or even a structure of nested
lists/dicts. Lists can be combined with the plus operator, and lists
and strings can be repeated with the multiply (star) operator. Class
methods are bound functions.

.. _pscript-caveats:

Caveats
-------

PScript fixes some of JS's quirks, but it's still just JavaScript.
Here's a list of things to keep an eye out for. This list is likely
incomplete. We recommend familiarizing yourself with JavaScript if you
plan to make heavy use of PScript.

* JavasScript has a concept of ``null`` (i.e. ``None``), as well as
  ``undefined``. Sometimes you may want to use ``if x is None or x is
  undefined: ...``.
* Accessing an attribute that does not exist will not raise an
  AttributeError but yield ``undefined``. Though this may change.
* Keys in a dictionary are implicitly converted to strings.
* Magic functions on classes (e.g. for operator overloading) do not work.
* Calling an object that starts with a capital letter is assumed to be
  a class instantiation (using ``new``): PScript classes *must* start
  with a capital letter, and any other callables must not.
* A function can accept keyword arguments if it has a ``**kwargs`` parameter
  or named arguments after ``*args``. Passing keywords to a function that does
  not handle keyword arguments might result in confusing errors.
* Divide by zero results in `inf` instead of raising ZeroDivisionError.
* In Python you can do `a_list += a_string` where each character in the string
  will be added to the list. In PScript this will convert `a_list` to a string.


PScript is valid Python
------------------------

Other than e.g. RapydScript, PScript is valid Python. This allows
creating modules that are a mix of real Python and PScript. You can easily
write code that runs correctly both as Python and PScript, and
:func:`raw JavaScript <pscript.RawJS>` can
be included where needed (e.g. for performance).

PScript's compiler is written in Python. Perhaps PScript can
at some point compile itself, so that it becomes possible to define
PScript inside HTML documents.

There are things you can do, which you cannot do in Python:


Performance
-----------

Because PScript produces relatively bare JavaScript, it is pretty fast.
Faster than CPython, and significantly faster than e.g. Brython.
Check out ``examples/app/benchmark.py``.

Nevertheless, the overhead to realize the more Pythonic behavior can
have a negative impact on performance in tight loops (in comparison to
writing the JS by hand). The recommended approach is to write
performance critical code in pure JavaScript
(using :func:`RawJS <pscript.RawJS>`) if necessary.


.. _pscript-overload:

Using PSCRIPT_OVERLOAD to increase performance
----------------------------------------------

To improve the performance of critical code, it's possible to disable
some of the overloading that make PScript more Pythonic. This increases
the speed of code, but it also makes it more like JavaScript.

To use this feature, write ``PSCRIPT_OVERLOAD = False``. Any code that
follows will not be subject to overloading. This parser setting can
only be used inside a function and applies only to (the scope of) that
function (i.e. not to functions defined inside that function nor any
outer scope). If needed, overloading can also be enabled again by
writing ``PSCRIPT_OVERLOAD = True``.

Things that are no longer overloaded:

* The add operator (``+``), so list concatenation cannot be done with ``+``.
* The multiply operator (``*``), so repeating a list or string cannot be done with ``*``.
* The equals operator (``==``), so deep comparisons of tuples/lists and dicts does not work.
* The implicit truthy operator (as e.g. used in an if-statement),
  so empty tuples/lists and dicts evaluate to True. Note that functions like
  ``bool()``, ``all()`` and ``any()`` still use the overloaded truthy.

.. _pscript-support:

Support
-------

This is an overview of the language features that PScript
supports/lacks.

Not currently supported:

* import (maybe we should translate an import to ``require()``?)
* the ``set`` class (JS has no set, but we could create one?)
* slicing with steps (JS does not support this)
* Generators, i.e. ``yield`` (not widely supported in JS)

Supported basics:

* numbers, strings, lists, dicts (the latter become JS arrays and objects)
* operations: binary, unary, boolean, power, integer division, ``in`` operator
* comparisons (``==`` -> ``==``, ``is`` -> ``===``)
* tuple packing and unpacking
* basic string formatting
* slicing with start end end (though not with step)
* if-statements and single-line if-expressions
* while-loops and for-loops supporting continue, break, and else-clauses
* for-loops using ``range()``
* for-loop over arrays
* for-loop over dict/object using ``.keys()``, ``.values()`` and ``.items()``
* function calls can have ``*args``
* function defs can have default arguments and ``*args``
* function calls/defs can use keyword arguments and ``**kwargs``, but
  use with care (see caveats).
* lambda expressions
* list comprehensions
* classes, with (single) inheritance, and the use of ``super()``
* raising and catching exceptions, assertions
* creation of "modules"
* globals / nonlocal
* The ``with`` statement (no equivalent in JS)
* double underscore name mangling

Supported Python conveniences:

* use of ``self`` is translated to ``this``
* ``print()`` becomes ``console.log()`` (also supports ``sep`` and ``end``)
* ``isinstance()`` Just Works (for primitive types as well as
  user-defined classes)
* an empty list or dict evaluates to False as in Python.
* all Python builtin functions that make sense in JS are supported:
  isinstance, issubclass, callable, hasattr, getattr, setattr, delattr,
  print, len, max, min, chr, ord, dict, list, tuple, range, pow, sum,
  round, int, float, str, bool, abs, divmod, all, any, enumerate, zip,
  reversed, sorted, filter, map.
* all methods of list, dict and str are supported (except a few string
  methods: encode, format_map, isprintable, maketrans).
* the default return value of a function is ``None``/``null`` instead
  of ``undefined``.
* list concatenation using the plus operator, and list/str repeating
  using the star operator.
* deep comparisons.
* class methods are bound functions (i.e. ``this`` is fixed to the
  instance).
* functions that are defined in another function (a.k.a closures) that do not
  have self/this as a first argument, are bound the the same instance as the
  function in which it is defined.


Other functionality
-------------------

The PScript package provides a few other "utilities" to deal with JS code,
such as renaming function/class definitions, and creating JS modules
(AMD, UMD, etc.).

"""

__version__ = '0.7.7'

import sys
import logging

logger = logging.getLogger(__name__)

# Assert compatibility and redirect to legacy version on Python 2.7
ok = True
if sys.version_info[0] == 2:  # pragma: no cover
    if sys.version_info < (2, 7):
        raise RuntimeError('PScript needs at least Python 2.7')
    if type(b'') == type(''):  # noqa - will be str and unicode after conversion
        sys.modules[__name__] = __import__(__name__ + '_legacy')
        ok = False

# NOTE: The code for the parser is quite long, especially if you want
# to document it well. Therefore it is split in multiple modules, which
# are simply numbered 0, 1, 2, etc. Here in the __init__, we define
# which parser is *the* parser. This gives us the freedom to split the
# parser in smaller pieces if we want.
#
# In the docstring of every parser module we maintain a brief user-guide
# demonstrating the features defined in that module. In the docs these
# docstrings are combined into one complete guide.

# flake8: noqa

if ok:

    from .parser0 import Parser0, JSError
    from .parser1 import Parser1
    from .parser2 import Parser2
    from .parser3 import Parser3
    from .base import *

    from .functions import py2js, evaljs, evalpy, JSString
    from .functions import script2js, js_rename, create_js_module
    from .stdlib import get_full_std_lib, get_all_std_names
    from .stubs import RawJS, JSConstant, window, undefined


del logging, sys, ok
