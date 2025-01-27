PScript
=======

[![Build Status](https://github.com/flexxui/pscript/workflows/CI/badge.svg)](https://github.com/flexxui/pscript/actions)
[![Documentation Status](https://readthedocs.org/projects/pscript/badge/?version=latest)](https://pscript.readthedocs.org)


PScript is a Python to JavaScript compiler, and is also the name of the subset
of Python that this compiler supports. It was originally developed as a part of
[Flexx]https://github.com/flexxui/flexx) and is now a project on its own.


Installation
------------

PScript is pure Python and requires Python 3.6+ (including Pypy).
It has no further dependencies.

```
pip install pscript
```


Short example
-------------

```py

   from pscript import py2js

   def foo(a, b=2):
      print(a - b)

   print(py2js(foo))
```

Gives:

```js
   var foo;
   foo = function flx_foo (a, b) {
      b = (b === undefined) ? 2: b;
      console.log((a - b));
      return null;
   };
```


Supported browsers
------------------

PScript aims to support all modern browsers, including Firefox, Chrome and Edge.
Internet Explorer is in principal supported from version 9, though some constructs
(e.g. ``async`` and ``await``) do not work in Internet Explorer.


PScript in the wild
-------------------

To give an idea of what PScript can do, here are some examples in the wild:

* Obviously, everything built in Flexx uses PScript, see e.g. [these examples](https://flexx.readthedocs.io/en/stable/examples/)
* The front-end of [TimeTagger.app](https://timetagger.app) is built in Python using PScript.

*Let us know if you know more!*


License
-------

PScript makes use of the liberal 2-clause BSD license. See LICENSE for details.
