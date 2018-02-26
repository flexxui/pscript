Welcome to PScript's documentation!
===================================

PScript is a Python to JavaScript compiler, and is also the name of the subset
of Python that this compiler supports. It was developed as a part of
`Flexx <http://flexx.live>`_ (as ``flexx.pyscript``) and is now represented
by its own project. Although it is still an important part of Flexx, it can
also be useful by itself.

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


Contents
--------

.. toctree::
   :maxdepth: 2
   
   intro
   api
   guide
   releasenotes


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
