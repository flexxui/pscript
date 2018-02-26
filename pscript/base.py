from .parser2 import Parser2
from .parser3 import Parser3


class BasicParser(Parser2):
    """ A parser without the Pythonic features for converting builtin
    functions and common methods.
    """
    pass


class Parser(Parser3):
    """ Parser to convert Python to JavaScript.
    
    Instantiate this class with the Python code. Retrieve the JS code
    using the dump() method.
    
    In a subclass, you can implement methods called "function_x" or
    "method_x", which will then be called during parsing when a
    function/method with name "x" is encountered. Several methods and
    functions are already implemented in this way.
    
    While working on ast parsing, this resource is very helpful:
    https://greentreesnakes.readthedocs.org
    
    Parameters:
        code (str): the Python source code.
        pysource (tuple): the filename and line number that contain the source.
        indent (int): the base indentation level (default 0). One
            indentation level means 4 spaces.
        docstrings (bool): whether docstrings are included in JS
            (default True).
        inline_stdlib (bool): whether the used stdlib functions are inlined
            (default True). Set to False if the stdlib is already loaded.
    """
    pass


# Create stubs that mean something
Infinity = float('inf')
NaN = float('nan')

def this_is_js():
    """ Function available in both JS and Py that returns whether the code is running
    on Python or JavaScript.
    """
    return False
