PScript API
===========

Convert Python to JavaScript
----------------------------


.. autofunction:: pscript.py2js

.. autofunction:: pscript.script2js


Evaluate JavaScript or Python in Node
-------------------------------------

.. autofunction:: pscript.evaljs

.. autofunction:: pscript.evalpy


More functions
--------------

.. autofunction:: pscript.js_rename

.. autofunction:: pscript.get_full_std_lib

.. autofunction:: pscript.get_all_std_names

.. autofunction:: pscript.create_js_module


The parser class
----------------

Most users probably want to use the above functions, but you can also
get closer to the metal by using and/or extending the parser class.

.. autoclass:: pscript.Parser


Embedding raw JavaScript
------------------------

PScript allows embedding raw JavaScript using the ``RawJS`` class.

.. autoclass:: pscript.RawJS


Dummy variables
---------------

The PScript module has a few dummy constants that can be imported and
used in your code to let e.g. pyflakes know that the variable exists. E.g.
``from pscript import undefined, window Infinity, NaN``.
Arbitrary dummy variables can be imported using
``from pscript.stubs import JSON, foo, bar``.

Marking a variable as global is also a good approach to tell pyflakes that
the variable exists.
