PScript
========

[![Build Status](https://travis-ci.org/flexxui/pscript.svg)](https://travis-ci.org/flexxui/pscript)
[![Documentation Status](https://readthedocs.org/projects/pscript/badge/?version=latest)](https://pscript.readthedocs.org)


PScript is a Python to JavaScript compiler, and is also the name of the subset
of Python that this compiler supports. It was developed as a part of
[Flexx](https://flexx.app) (as `flexx.pyscript`) and is now represented
by its own project. Although it is still an important part of Flexx, it can
also be useful by itself.


Installation
------------

PScript is pure Python and requires Python 2.7 or 3.5+ (including Pypy).
It has no further dependencies.

* ``pip install pscript``, or
* ``conda install pscript -c conda-forge``



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


License
-------

PScript makes use of the liberal 2-clause BSD license. See LICENSE for details.
