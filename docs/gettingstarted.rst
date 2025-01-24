Getting started
===============

Installation
------------

PScript has no dependencies except Python. It requires Python 3.6+.
Use either of these to install PScript:

    * ``pip install pscript``
    * ``conda install pscript``


Basic usage
-----------

The main function to use is the :func:`py2js <pscript.py2js>` function.

A short example:

.. code-block:: py

   from pscript import py2js

   def foo(a, b=2):
      print(a - b)

   print(py2js(foo))

Gives:

.. code-block:: js

   var foo;
   foo = function flx_foo (a, b) {
      b = (b === undefined) ? 2: b;
      console.log((a - b));
      return null;
   };
