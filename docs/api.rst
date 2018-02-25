PScript API
===========

.. autofunction:: pscript.py2js

.. autofunction:: pscript.evaljs

.. autofunction:: pscript.evalpy

.. autofunction:: pscript.script2js

.. autofunction:: pscript.js_rename

.. autofunction:: pscript.get_full_std_lib

.. autofunction:: pscript.get_all_std_names

.. autofunction:: pscript.create_js_module

----

Most users probably want to use the above functions, but you can also
get closer to the metal by using and/or extending the parser class.

.. autoclass:: pscript.Parser

----

PScript allows embedding raw JavaScript using the ``RawJS`` class.

.. autoclass:: pscript.RawJS

----

The PScript module has a few dummy constants that can be imported and
used in your code to let e.g. pyflakes know that the variable exists. E.g.
``from pscript import undefined, window Infinity, NaN``.
Arbitrary dummy variables can be imported using
``from pscript.stubs import JSON, foo, bar``.

Marking a variable as global is also a good approach to tell pyflakes that
the variable exists.
