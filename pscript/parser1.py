"""

The basics
----------

Most types just work, common Python names are converted to their JavaScript
equivalents.

.. pscript_example::

    # Simple operations
    3 + 4 -1
    3 * 7 / 9
    5**2
    pow(5, 2)
    7 // 2

    # Basic types
    [True, False, None]

    # Lists and dicts
    foo = [1, 2, 3]
    bar = {'a': 1, 'b': 2}


Slicing and subscriping
-----------------------

.. pscript_example::

    # Slicing lists
    foo = [1, 2, 3, 4, 5]
    foo[2:]
    foo[2:-2]

    # Slicing strings
    bar = 'abcdefghij'
    bar[2:]
    bar[2:-2]

    # Subscripting
    foo = {'bar': 3}
    foo['bar']
    foo.bar  # Works in JS, but not in Python


String formatting
-----------------

String formatting is supported in various forms.

.. pscript_example::

    # Old school
    "value: %g" % val
    "%s: %0.2f" % (name, val)

    # Modern
    "value: {:g}".format(val)
    "{}: {:3.2f}".format(name, val)

    # F-strings (python 3.6+)
    #f"value: {val:g}"
    #f"{name}: {val:3.2f}"

    # This also works
    t = "value: {:g}"
    t.format(val)

    # But this does not (because PScript cannot know whether t is str or float)
    t = "value: %g"
    t % val

Kinds of formatting that is supported:

* Float, exponential en "general" number formatting.
* Specifying precision for numbers.
* Padding of number with "+" or " ".
* Repr-formatting.

At the moment, PScript does not support advanced features such as string
padding.


Assignments
-----------

Declaration of variables is handled automatically. Also support for
tuple packing and unpacking (a.k.a. destructuring assignment).

.. pscript_example::

    # Declare foo
    foo = 3

    # But not here
    bar.foo = 3

    # Pack items in an array
    a = 1, 2, 3

    # And unpack them
    a1, a2, a3 = a

    # Deleting variables
    del bar.foo

    # Functions starting with a capital letter
    # are assumed constructors
    foo = Foo()


Comparisons
-----------

.. pscript_example::

    # Identity
    foo is bar

    # Equality
    foo == bar

    # But comparisons are deep (unlike JS)
    (2, 3, 4) == (2, 3, 4)
    (2, 3) in [(1,2), (2,3), (3,4)]

    # Test for null
    foo is None

    # Test for JS undefined
    foo is undefined

    # Testing for containment
    "foo" in "this has foo in it"
    3 in [0, 1, 2, 3, 4]


Truthy and Falsy
----------------

In JavaScript, an empty array and an empty dict are interpreted as
truthy. PScript fixes this, so that you can do ``if an_array:`` as
usual.

.. pscript_example::

    # These evaluate to False:
    0
    NaN
    ""  # empty string
    None  # JS null
    undefined
    []
    {}

    # This still works
    a = []
    a = a or [1]  # a is now [1]


Function calls
--------------

As in Python, the default return value of a function is ``None`` (i.e.
``null`` in JS).

.. pscript_example::

    # Business as usual
    foo(a, b)

    # Support for star args (but not **kwargs)
    foo(*a)

Imports
-------

Imports are not supported syntax in PScript. Imports "from pscript"
and "from __future__" are ignored to help writing hybrid Python/JS
modules.

PScript does provide functionality to package code in JS modules,
but these follow the ``require`` pattern.

"""

import re

from . import commonast as ast
from . import stdlib
from .parser0 import Parser0, JSError, unify, reprs


# Define builtin stuff for which we know that it returns a bool or int
_bool_funcs = "hasattr", "all", "any", "op_contains", "op_equals", "truthy"
_bool_meths = (
    "count",
    "isalnum",
    "isalpha",
    "isidentifier",
    "islower",
    "isnumeric",
    "isdigit",
    "isdecimal",
    "isspace",
    "istitle",
    "isupper",
    "startswith",
)
returning_bool = tuple(
    [stdlib.FUNCTION_PREFIX + x + "(" for x in _bool_funcs]
    + [stdlib.METHOD_PREFIX + x + "." for x in _bool_meths]
)


# precompile regexp to help determine whether a string is an identifier
isidentifier1 = re.compile(r"^\w+$", re.UNICODE)

reserved_names = (
    "abstract",
    "instanceof",
    "boolean",
    "enum",
    "switch",
    "export",
    "interface",
    "synchronized",
    "extends",
    "let",
    "case",
    "throw",
    "catch",
    "final",
    "native",
    "throws",
    "new",
    "transient",
    "const",
    "package",
    "function",
    "private",
    "typeof",
    "debugger",
    "goto",
    "protected",
    "var",
    "default",
    "public",
    "void",
    "delete",
    "implements",
    "volatile",
    "do",
    "static",
    # Commented, because are disallowed in Python too.
    # 'else', 'break', 'finally', 'class', 'for', 'try', 'continue', 'if',
    # 'return', 'import', 'while', 'in', 'with',
    # Commented for pragmatic reasons
    # 'super', 'float', 'this', 'int', 'byte', 'long', 'char', 'short',
    # 'double', 'null', 'true', 'false',
)


class Parser1(Parser0):
    """Parser that add basic functionality like assignments,
    operations, function calls, and indexing.
    """

    @property
    def _pscript_overload(self):
        """Whether pscript overloads add, mul, equals, and truthy.
        This setting applies per scope.
        """
        return self._stack[-1][2]._pscript_overload

    ## Literals

    def parse_Num(self, node):
        return repr(node.value)

    def parse_Str(self, node):
        return reprs(node.value)

    def parse_JoinedStr(self, node):
        parts, value_nodes = [], []
        for n in node.value_nodes:
            if isinstance(n, ast.Str):
                parts.append(n.value)
            else:
                assert isinstance(n, ast.FormattedValue)
                parts.append("{" + self._parse_FormattedValue_fmt(n) + "}")
                value_nodes.append(n.value_node)
        thestring = reprs("".join(parts))
        return self.use_std_method(thestring, "format", value_nodes)

    def parse_FormattedValue(self, node):  # can als be present standalone
        thestring = "{" + self._parse_FormattedValue_fmt(node) + "}"
        return self.use_std_method(thestring, "format", [node.value_node])

    def _parse_FormattedValue_fmt(self, node):
        """Return fmt for a FormattedValue node."""
        fmt = ""
        if node.conversion:
            fmt += "!" + node.conversion
        if node.format_node and len(node.format_node.value_nodes) > 0:
            if len(node.format_node.value_nodes) > 1:
                raise JSError("String formatting only supports singleton format spec.")
            spec_node = node.format_node.value_nodes[0]
            if not isinstance(spec_node, ast.Str):
                raise JSError("String formatting only supports string format spec.")
            fmt += ":" + spec_node.value
        return fmt

    def parse_Bytes(self, node):
        raise JSError("No Bytes in JS")

    def parse_NameConstant(self, node):
        M = {True: "true", False: "false", None: "null"}
        return M[node.value]

    def parse_List(self, node):
        code = ["["]
        for child in node.element_nodes:
            code += self.parse(child)
            code.append(", ")
        if node.element_nodes:
            code.pop(-1)  # skip last comma
        code.append("]")
        return code

    def parse_Tuple(self, node):
        return self.parse_List(node)  # tuple = ~ list in JS

    def parse_Dict(self, node):
        # Oh JS; without the outer braces, it would only be an Object if used
        # in an assignment ...
        use_make_dict_func = False
        code = ["({"]
        for key, val in zip(node.key_nodes, node.value_nodes):
            if isinstance(key, (ast.Num, ast.NameConstant)):
                code += self.parse(key)
            elif (
                isinstance(key, ast.Str)
                and isidentifier1.match(key.value)
                and key.value[0] not in "0123456789"
            ):
                code += key.value
            else:
                use_make_dict_func = True
                break
            code.append(": ")
            code += self.parse(val)
            code.append(", ")
        if node.key_nodes:
            code.pop(-1)  # skip last comma
        code.append("})")

        # Do we need to use the fallback?
        if use_make_dict_func:
            func_args = []
            for key, val in zip(node.key_nodes, node.value_nodes):
                func_args += [unify(self.parse(key)), unify(self.parse(val))]
            self.use_std_function("create_dict", [])
            return stdlib.FUNCTION_PREFIX + "create_dict(" + ", ".join(func_args) + ")"
        return code

    def parse_Set(self, node):
        raise JSError("No Set in JS")

    ## Variables

    def push_scope_prefix(self, prefix):
        # To avoid name clashes e.g. in comprehensions, which have their own
        # scope in Python, but we want to apply these as a for loop in JS
        # where possible.
        assert prefix
        self._scope_prefix.append(prefix)

    def pop_scope_prefix(self):
        self._scope_prefix.pop(-1)

    def parse_Name(self, node, fullname=None):
        # node.ctx can be Load, Store, Del -> can be of use somewhere?
        name = node.name
        if name in reserved_names:
            raise JSError("Cannot use reserved name %s as a variable name!" % name)
        if self.vars.is_known(name):
            return self.with_prefix(name)
        if self._scope_prefix:
            for stackitem in reversed(self._stack):
                scope = stackitem[2]
                for prefix in reversed(self._scope_prefix):
                    prefixed_name = prefix + name
                    if prefixed_name in scope:
                        return prefixed_name
        if name in self.NAME_MAP:
            return self.NAME_MAP[name]
        # Else ...
        if not (name in self._functions or name in ("undefined", "window")):
            # mark as used (not defined)
            used_name = (name + "." + fullname) if fullname else name
            self.vars.use(name, used_name)
        return name

    def parse_Starred(self, node):
        # they're present in Call arguments, but we parse them there.
        raise JSError("Starred args are not supported.")

    ## Expressions

    def parse_Expr(self, node):
        # Expression (not stored in a variable)
        code = [self.lf()]
        code += self.parse(node.value_node)
        code.append(";")
        return code

    def parse_UnaryOp(self, node):
        if node.op == node.OPS.Not:
            return "!", self._wrap_truthy(node.right_node)
        else:
            op = self.UNARY_OP[node.op]
            right = unify(self.parse(node.right_node))
            return op, right

    def parse_BinOp(self, node):
        if node.op == node.OPS.Mod and isinstance(node.left_node, ast.Str):
            # Modulo on a string is string formatting in Python
            return self._format_string(node)

        left = unify(self.parse(node.left_node))
        right = unify(self.parse(node.right_node))

        if node.op == node.OPS.Add:
            C = ast.Num, ast.Str
            if self._pscript_overload and not (
                isinstance(node.left_node, C)
                or isinstance(node.right_node, C)
                or (
                    isinstance(node.left_node, ast.BinOp)
                    and node.left_node.op == node.OPS.Add
                    and "op_add" not in left
                )
                or (
                    isinstance(node.right_node, ast.BinOp)
                    and node.right_node.op == node.OPS.Add
                    and "op_add" not in right
                )
            ):
                return self.use_std_function("op_add", [left, right])
        elif node.op == node.OPS.Mult:
            C = ast.Num
            if self._pscript_overload and not (
                isinstance(node.left_node, C) and isinstance(node.right_node, C)
            ):
                return self.use_std_function("op_mult", [left, right])
        elif node.op == node.OPS.Pow:
            return ["Math.pow(", left, ", ", right, ")"]
        elif node.op == node.OPS.FloorDiv:
            return ["Math.floor(", left, "/", right, ")"]

        op = " %s " % self.BINARY_OP[node.op]
        return [left, op, right]

    def _format_string(self, node):
        # Get value_nodes
        if isinstance(node.right_node, (ast.Tuple, ast.List)):
            value_nodes = node.right_node.element_nodes
        else:
            value_nodes = [node.right_node]

        # Is the left side a string? If not, exit early
        # This works, but we cannot know whether the left was a string or number :P
        # if not isinstance(node.left_node, ast.Str):
        #     thestring = unify(self.parse(node.left_node))
        #     thestring += ".replace(/%([0-9\.\+\-\#]*[srdeEfgGioxXc])/g, '{:$1}')"
        #     return self.use_std_method(thestring, 'format', value_nodes)

        assert isinstance(node.left_node, ast.Str)
        left = "".join(self.parse(node.left_node))
        sep, left = left[0], left[1:-1]

        # Get matches
        matches = list(re.finditer(r"%[0-9\.\+\-\#]*[srdeEfgGioxXc]", left))
        if len(matches) != len(value_nodes):
            raise JSError(
                "In string formatting, number of placeholders "
                "does not match number of replacements"
            )
        # Format
        parts = []
        start = 0
        for m in matches:
            fmt = m.group(0)
            fmt = {"%r": "!r", "%s": ""}.get(fmt, ":" + fmt[1:])
            # Add the part in front of the match (and after prev match)
            parts.append(left[start : m.start()])
            parts.append("{%s}" % fmt)
            start = m.end()
        parts.append(left[start:])
        thestring = sep + "".join(parts) + sep
        return self.use_std_method(thestring, "format", value_nodes)

    def _wrap_truthy(self, node):
        """Wraps an operation in a truthy call, unless its not necessary."""
        eq_name = stdlib.FUNCTION_PREFIX + "op_equals"
        test = "".join(self.parse(node))
        if not self._pscript_overload:
            return unify(test)
        elif (
            test.endswith(".length")
            or test.startswith("!")
            or test.isnumeric()
            or test == "true"
            or test == "false"
            or test.count("==")
            or test.count(">")
            or test.count("<")
            or test.count(eq_name)
            or test == '"this_is_js()"'
            or test.startswith("Array.isArray(")
            or (test.startswith(returning_bool) and "||" not in test)
        ):
            return unify(test)
        else:
            return self.use_std_function("truthy", [test])

    def parse_BoolOp(self, node):
        op = " %s " % self.BOOL_OP[node.op]
        if node.op.lower() == "or":  # allow foo = bar or []
            values = [unify(self._wrap_truthy(val)) for val in node.value_nodes[:-1]]
            values += [unify(self.parse(node.value_nodes[-1]))]
        else:
            values = [unify(self._wrap_truthy(val)) for val in node.value_nodes]
        return op.join(values)

    def parse_Compare(self, node):
        left = unify(self.parse(node.left_node))
        right = unify(self.parse(node.right_node))

        if node.op in (node.COMP.Eq, node.COMP.NotEq) and not left.endswith(".length"):
            if self._pscript_overload:
                code = self.use_std_function("op_equals", [left, right])
                if node.op == node.COMP.NotEq:
                    code = "!" + code
            else:
                if node.op == node.COMP.NotEq:
                    code = [left, "!=", right]
                else:
                    code = [left, "==", right]
            return code
        elif node.op in (node.COMP.In, node.COMP.NotIn):
            self.use_std_function("op_equals", [])  # trigger use of equals
            code = self.use_std_function("op_contains", [left, right])
            if node.op == node.COMP.NotIn:
                code = "!" + code
            return code
        else:
            op = self.COMP_OP[node.op]
            return "%s %s %s" % (left, op, right)

    def parse_Call(self, node):
        # Get full function name and method name if it exists

        if isinstance(node.func_node, ast.Attribute):
            # We dont want to parse twice, because it may add to the vars_unknown
            method_name = node.func_node.attr
            nameparts = self.parse(node.func_node)
            full_name = unify(nameparts)
            nameparts[-1] = nameparts[-1].rsplit(".", 1)[0]
            base_name = unify(nameparts)
        elif isinstance(node.func_node, ast.Subscript):
            base_name = unify(self.parse(node.func_node.value_node))
            full_name = unify(self.parse(node.func_node))
            method_name = ""
        else:  # ast.Name
            method_name = ""
            base_name = ""
            full_name = unify(self.parse(node.func_node))

        # Handle special functions and methods
        res = None
        if method_name in self._methods:
            res = self._methods[method_name](node, base_name)
        elif full_name in self._functions:
            res = self._functions[full_name](node)
        if res is not None:
            return res

        # Handle normally
        if base_name.endswith("._base_class") or base_name == "super()":
            # super() was used, use "call" to pass "this"
            return [full_name] + self._get_args(node, "this", True)
        else:
            code = [full_name] + self._get_args(node, base_name)
            # Insert "new" if this looks like a class
            if base_name == "this":
                pass
            elif method_name:
                if method_name[0].lower() != method_name[0]:
                    code.insert(0, "new ")
            else:
                fn = full_name
                if fn in self._seen_func_names and fn not in self._seen_class_names:
                    pass
                elif fn not in self._seen_func_names and fn in self._seen_class_names:
                    code.insert(0, "new ")
                elif full_name[0].lower() != full_name[0]:
                    code.insert(0, "new ")
            return code

    def _get_args(self, node, base_name, use_call_or_apply=False):
        """Get arguments for function call. Does checking for keywords and
        handles starargs. The first element in the returned list is either
        "(" or ".apply(".
        """

        # Can produce:
        # normal:               foo(.., ..)
        # use_call_or_apply:    foo.call(base_name, .., ..)
        # use_starargs:         foo.apply(base_name, vararg_name)
        #           or:         foo.apply(base_name, [].concat([.., ..], vararg_name)
        # has_kwargs:           foo({__args: [], __kwargs: {} })
        #         or:           foo.apply(base_name, ({__args: [], __kwargs: {} })

        base_name = base_name or "null"

        # Get arguments
        args_simple, args_array = self._get_positional_args(node)
        kwargs = self._get_keyword_args(node)

        if kwargs is not None:
            # Keyword arguments need a whole special treatment
            if use_call_or_apply:
                start = [".call(", base_name, ", "]
            else:
                start = ["("]
            return start + [
                "{",
                "flx_args: ",
                args_array,
                ", flx_kwargs: ",
                kwargs,
                "})",
            ]
        elif args_simple is None:
            # Need to use apply
            return [".apply(", base_name, ", ", args_array, ")"]
        elif use_call_or_apply:
            # Need to use call (arg_simple can be empty string)
            if args_simple:
                return [".call(", base_name, ", ", args_simple, ")"]
            else:
                return [".call(", base_name, ")"]
        else:
            # Normal function call
            return ["(", args_simple, ")"]

    def _get_positional_args(self, node):
        """Returns:
        * a string args_simple, which represents the positional args in comma
          separated form. Can be None if the args cannot be represented that
          way. Note that it can be empty string.
        * a string args_array representing the array with positional arguments.
        """

        # Generate list of arg lists (has normal positional args and starargs)
        # Note that there can be multiple starargs and these can alternate.
        argswithcommas = []
        arglists = [argswithcommas]
        for arg in node.arg_nodes:
            if isinstance(arg, ast.Starred):
                starname = "".join(self.parse(arg.value_node))
                arglists.append(starname)
                argswithcommas = []
                arglists.append(argswithcommas)
            else:
                argswithcommas.extend(self.parse(arg))
                argswithcommas.append(", ")

        # Clear empty lists and trailing commas
        for i in reversed(range(len(arglists))):
            arglist = arglists[i]
            if not arglist:
                arglists.pop(i)
            elif arglist[-1] == ", ":
                arglist.pop(-1)

        # Generate code for positional arguments
        if len(arglists) == 0:
            return "", "[]"
        elif len(arglists) == 1 and isinstance(arglists[0], list):
            args_simple = "".join(argswithcommas)
            return args_simple, "[" + args_simple + "]"
        elif len(arglists) == 1:
            assert isinstance(arglists[0], str)
            return None, arglists[0]
        else:
            code = ["[].concat("]
            for arglist in arglists:
                if isinstance(arglist, list):
                    code += ["["]
                    code += arglist
                    code += ["]"]
                else:
                    code += [arglist]
                code += [", "]
            code.pop(-1)
            code += ")"
            return None, "".join(code)

    def _get_keyword_args(self, node):
        """Get a string that represents the dictionary of keyword arguments,
        or None if there are no keyword arguments (normal nor double-star).
        """

        # Collect elements that will make up the total kwarg dict
        kwargs = []
        for kwnode in node.kwarg_nodes:
            if not kwnode.name:  # **xx
                kwargs.append(unify(self.parse(kwnode.value_node)))
            else:  # foo=xx
                if not (kwargs and isinstance(kwargs[-1], list)):
                    kwargs.append([])
                kwargs[-1].append(
                    "%s: %s" % (kwnode.name, unify(self.parse(kwnode.value_node)))
                )

        # Resolve sequneces of loose kwargs
        for i in range(len(kwargs)):
            if isinstance(kwargs[i], list):
                kwargs[i] = "{" + ", ".join(kwargs[i]) + "}"

        # Compose, easy if singleton, otherwise we need to merge
        if len(kwargs) == 0:
            return None
        elif len(kwargs) == 1:
            return kwargs[0]
        else:
            # register use of merge_dicts(), but we build the string ourselves
            self.use_std_function("merge_dicts", [])
            return stdlib.FUNCTION_PREFIX + "merge_dicts(" + ", ".join(kwargs) + ")"

    def parse_Attribute(self, node, fullname=None):
        fullname = node.attr + "." + fullname if fullname else node.attr
        if isinstance(node.value_node, ast.Name):
            base_name = self.parse_Name(node.value_node, fullname)
        elif isinstance(node.value_node, ast.Attribute):
            base_name = self.parse_Attribute(node.value_node, fullname)
        else:
            base_name = unify(self.parse(node.value_node))
        attr = node.attr
        # Double underscore name mangling
        if attr.startswith("__") and not attr.endswith("__") and base_name == "this":
            for i in range(len(self._stack) - 1, -1, -1):
                if self._stack[i][0] == "class":
                    classname = self._stack[i][1]
                    attr = "_" + classname + attr
                    break
        if attr in self.ATTRIBUTE_MAP:
            return self.ATTRIBUTE_MAP[attr].replace("{}", base_name)
        else:
            return "%s.%s" % (base_name, attr)

    ## Statements

    def parse_Assign(self, node):
        """Variable assignment."""
        code = [self.lf()]

        # Set PScript behavior? Note that its reset on a function exit.
        if (
            len(node.target_nodes) == 1
            and isinstance(node.target_nodes[0], ast.Name)
            and node.target_nodes[0].name == "PSCRIPT_OVERLOAD"
        ):
            if self._stack[-1][0] != "function":
                raise JSError("Can only set PSCRIPT_OVERLOAD inside a function")
            if not isinstance(node.value_node, ast.NameConstant):
                raise JSError("Can only set PSCRIPT_OVERLOAD with a bool")
            else:
                self._stack[-1][2]._pscript_overload = bool(node.value_node.value)
                return []

        # Parse targets
        tuple = []
        for target in node.target_nodes:
            var = "".join(self.parse(target))
            if isinstance(target, ast.Name):
                if "." in var:
                    code.append(var)
                else:
                    self.vars.add(var)
                    code.append(self.with_prefix(var))
            elif isinstance(target, ast.Attribute):
                code.append(var)
            elif isinstance(target, ast.Subscript):
                code.append(var)
            elif isinstance(target, (ast.Tuple, ast.List)):
                dummy = self.dummy()
                code.append(dummy)
                tuple = target.element_nodes
            else:
                raise JSError("Unsupported assignment type")
            code.append(" = ")

        # Parse right side
        if isinstance(node.value_node, ast.ListComp) and len(node.target_nodes) == 1:
            result_name = self.dummy()
            code.append(result_name + ";")
            lc_code = self.parse_ListComp_funtionless(node.value_node, result_name)
            code = [self.lf(), result_name + " = [];"] + lc_code + code
        else:
            code += self.parse(node.value_node)
            code.append(";")

        # Handle tuple unpacking
        if tuple:
            code.append(self.lf())
            for i, x in enumerate(tuple):
                var = unify(self.parse(x))
                if isinstance(x, ast.Name):  # but not when attr or index
                    self.vars.add(var)
                code.append("%s = %s[%i];" % (var, dummy, i))

        return code

    def parse_AugAssign(self, node):  # -> x += 1
        target = "".join(self.parse(node.target_node))
        value = "".join(self.parse(node.value_node))

        nl = self.lf()
        if (
            node.op == node.OPS.Add
            and self._pscript_overload
            and not isinstance(node.value_node, (ast.Num, ast.Str))
        ):
            return [
                nl,
                target,
                " = ",
                self.use_std_function("op_add", [target, value]),
                ";",
            ]
        elif node.op == node.OPS.Mult and self._pscript_overload:
            return [
                nl,
                target,
                " = ",
                self.use_std_function("op_mult", [target, value]),
                ";",
            ]
        elif node.op == node.OPS.Pow:
            return [nl, target, " = Math.pow(", target, ", ", value, ");"]
        elif node.op == node.OPS.FloorDiv:
            return [nl, target, " = Math.floor(", target, "/", value, ");"]
        else:
            op = " %s= " % self.BINARY_OP[node.op]
            return [nl, target, op, value, ";"]

    def parse_Delete(self, node):
        code = []
        for target in node.target_nodes:
            code.append(self.lf("delete "))
            code += self.parse(target)
            code.append(";")
        return code

    def parse_Pass(self, node):
        return []

    ## Subscripting

    def parse_Subscript(self, node):
        value_list = self.parse(node.value_node)
        slice_list = self.parse(node.slice_node)

        code = []
        code += value_list

        if isinstance(node.slice_node, (ast.Slice, ast.Tuple)):
            code.append(".slice(")
            code += slice_list
            code.append(")")
        else:
            code.append("[")
            if slice_list[0].startswith("-"):
                code.append(unify(value_list) + ".length ")
            code += slice_list
            code.append("]")
        return code

    def parse_Index(self, node):
        return self.parse(node.value_node)

    def parse_Slice(self, node):
        code = []
        if node.step_node:
            raise JSError("Slicing with step not supported.")
        if node.lower_node:
            code += self.parse(node.lower_node)
        else:
            code.append("0")
        if node.upper_node:
            code.append(",")
            code += self.parse(node.upper_node)
        return code

    def parse_ExtSlice(self, node):
        raise JSError("Multidimensional slicing not supported in JS")

    ## Imports

    def parse_Import(self, node):
        if node.root and "pscript" in node.root:
            # User is probably importing names from here to allow
            # writing the JS code and command to parse it in one module.
            # Ignore this import.
            return []
        if node.root and node.root == "__future__":
            return []  # stuff to help the parser
        if node.root == "time":
            return []  # PScript natively supports time() and perf_counter()
        if node.root == "typing":
            # User is probably importing type annotations. Ignore this import.
            return []
        raise JSError("PScript does not support imports.")

    def parse_Module(self, node):
        # Module level. Every piece of code has a module as the root.
        # Just pass body.

        # Get docstring, but only if in module mode
        # module_mode = self._stack[0][1] # top stack has a name -> works no more
        module_mode = self._pysource and self._pysource[1] == 0  # line nr offset
        docstring = ""
        if self._docstrings and module_mode:
            docstring = self.pop_docstring(node)

        code = []
        if docstring:
            for line in docstring.splitlines():
                code.append(self.lf("// " + line))
            code.append("\n")
        for child in node.body_nodes:
            code += self.parse(child)
        return code
