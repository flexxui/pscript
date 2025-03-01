"""Tests for PScript functions"""

# ruff: noqa: F841

import os
import tempfile

from pscript.testing import run_tests_if_main, raises

from pscript import py2js, evaljs, evalpy, script2js


def test_dotted_unknowns():
    def func1():
        x = ui._layouts.SomeLayout()  # noqa
        y = ui.SomeLayout.YYY  # noqa
        z = ui.SomeOtherLayout  # noqa

    js = py2js(func1)
    assert js.meta["vars_unknown"] == set(
        ["ui._layouts.SomeLayout", "ui.SomeLayout.YYY", "ui.SomeOtherLayout"]
    )


def test_py2js_on_wrong_vals():
    raises(ValueError, py2js, [])
    raises(ValueError, py2js, {})

    raises(ValueError, py2js, str)  # cannot find source for str


def test_py2js_on_strings():
    # No need for extensive testing; we use this function extensively
    # in the other tests ...
    assert py2js("3 + 3") == "3 + 3;"
    assert py2js("list()") == "[];"


def test_evaljs():
    assert evaljs("3+4") == "7"
    assert evaljs("var x = {}; x.doesnotexist") == ""  # strip undefined


def test_evalpy():
    assert evalpy("[3, 4]") == "[ 3, 4 ]"
    assert evalpy("[3, 4]", False) == "[3,4]"


def test_py2js_on_function():
    def foo():
        pass

    # normal
    jscode = py2js(foo)
    assert jscode.startswith("var foo")
    assert jscode.meta["pycode"].startswith("def foo")

    # renamed
    jscode = py2js(foo, "bar")
    assert jscode.meta["pycode"].startswith("def foo")
    assert "foo" not in jscode
    assert jscode.startswith("var bar")
    assert "bar = function " in jscode

    # renamed 2
    jscode = py2js(foo, "bar.bla")
    assert jscode.meta["pycode"].startswith("def foo")
    assert "foo" not in jscode
    assert "var bar.bla" not in jscode
    assert "bar.bla = function " in jscode

    # Skip decorators
    stub1 = lambda x: x
    stub2 = lambda x=None: stub1

    @stub1
    @stub1
    def foo1():
        pass

    @stub2()
    def foo2():
        pass

    @py2js
    def foo3():
        pass

    @py2js(indent=1)
    def foo4():
        pass

    assert callable(foo1)
    assert callable(foo2)
    assert py2js(foo1).meta["pycode"].startswith("def foo")
    assert py2js(foo2).meta["pycode"].startswith("def foo")
    assert foo3.startswith("var foo3")
    assert foo4.startswith("    var foo4")


def test_py2js_on_class():
    class Foo1:
        X = 3

        def spam():
            pass

    # normal
    jscode = py2js(Foo1, inline_stdlib=False)
    assert jscode.startswith("var Foo1")
    assert jscode.meta["pycode"].startswith("class Foo1")

    # renamed
    jscode = py2js(Foo1, "Bar", inline_stdlib=False)
    assert jscode.meta["pycode"].startswith("class Foo")
    assert "Foo" not in jscode
    assert jscode.startswith("var Bar")

    # renamed 2
    jscode = py2js(Foo1, "Bar.bla", inline_stdlib=False)
    assert jscode.meta["pycode"].startswith("class Foo")
    assert "Foo" not in jscode
    assert "var Bar.bla" not in jscode
    assert "Bar.bla = function " in jscode


class Foo2:
    __x = 42
    __y__ = 7

    def res1(self):
        return self.__x

    def res2(self):
        return self.__y__


def foo1():
    return 42


def foo2(self):
    return self.__x + self.__y__


# Function name not compliant with PEP8 but that happens.
def Foo3():
    return "a"


def test_py2js_rename_class():
    code = py2js(Foo2, "Bar")
    assert "foo" not in code.lower()
    assert evaljs(code + "var m=new Bar(); [m.res1(), m.res2()];") == "[ 42, 7 ]"

    code = py2js(Foo2, "xx.Bar")
    assert "foo" not in code.lower()
    assert (
        evaljs("var xx={};\n" + code + "var m=new xx.Bar(); [m.res1(), m.res2()];")
        == "[ 42, 7 ]"
    )


def test_py2s_rename_function():
    code = py2js(foo1, "bar")
    assert "foo" not in code.lower()
    assert evaljs(code + "bar()") == "42"

    code = py2js(foo1, "xx.bar")
    assert "foo" not in code.lower()
    assert evaljs("var xx={};\n" + code + "xx.bar();") == "42"

    code = py2js(Foo3, "bar")
    assert "foo" not in code.lower()
    assert evaljs(code + "bar()") == "a"


def test_py2s_rename_function_to_method():
    code1 = py2js(Foo2, "Bar")
    code = code1 + py2js(foo2, "Bar.prototype.bar")
    assert "foo" not in code.lower()
    assert evaljs(code + "var m=new Bar(); m.bar();") == "49"

    code1 = py2js(Foo2, "Bar")
    code = code1 + "\nvar $Bar = Bar.prototype;\n" + py2js(foo2, "$Bar.bar")
    assert "foo" not in code.lower()
    assert evaljs(code + "var m=new Bar(); m.bar();") == "49"

    code1 = py2js(Foo2, "xx.Bar")
    code = code1 + py2js(foo2, "xx.Bar.prototype.bar")
    assert "foo" not in code.lower()
    assert evaljs("var xx={};\n" + code + "var m=new xx.Bar(); m.bar();") == "49"


def test_raw_js():
    def func(a, b):
        """
        var c = 3;
        return a + b + c;
        """

    code = py2js(func)
    assert evaljs(code + "func(100, 10)") == "113"
    assert evaljs(code + 'func("x", 10)') == "x103"


TEST_CODE = """

var foo = function () {};

var foo = function () {};

var f1;
f1 = function () {
    var foo = function () {};
    var bar = function () {};
}

var f2;
f2 = function () {
    var foo = function () {};
    var bar = function () {};
}
"""

# def test_clean_code():
#
#     code = clean_code(TEST_CODE)
#     assert code.count('var foo =') == 1
#     assert code.count('var bar =') == 2


def test_scripts():
    # Prepare
    pycode = "foo = 42; print(foo)"
    pyname = os.path.join(tempfile.gettempdir(), "pscript_test.py")
    with open(pyname, "wb") as f:
        f.write(pycode.encode())
    jsname = pyname[:-3] + ".js"

    # Convert - plain file (no module)
    script2js(pyname)

    # Check result
    jscode = open(jsname, "rb").read().decode()
    assert "foo = 42;" in jscode
    assert "define(" not in jscode

    # Convert - module light
    script2js(pyname, "mymodule", module_type="simple")

    # Check result
    jscode = open(jsname, "rb").read().decode()
    assert "foo = 42;" in jscode
    assert "define(" not in jscode

    # Convert - module UMD
    script2js(pyname, "mymodule", module_type="umd")

    # Check result
    jscode = open(jsname, "rb").read().decode()
    assert "foo = 42;" in jscode
    assert "define(" in jscode
    assert "module.exports" in jscode
    assert "root.mymodule" in jscode

    # Convert - no module, explicit file
    script2js(pyname, None, jsname)

    # Check result
    jscode = open(jsname, "rb").read().decode()
    assert "foo = 42;" in jscode
    assert "define(" not in jscode


run_tests_if_main()
