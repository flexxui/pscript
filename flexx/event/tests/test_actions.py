"""
Test actions.
"""

from flexx.util.testing import run_tests_if_main, skipif, skip, raises
from flexx.event.both_tester import run_in_both, this_is_js

from flexx import event

loop = event.loop


class MyObject(event.Component):
    
    foo = event.Property()
    
    @event.action
    def set_foo(self, v):
        self._mutate_foo(v)
    
    @event.action
    def set_foo_add(self, *args):
        self._mutate_foo(sum(args))
    
    @event.action
    def increase_foo(self):
        self.set_foo(self.foo + 1)  # mutation will be applied *now*
        self.set_foo(self.foo + 1)  # ... so we increase by 2
    
    @event.action
    def do_silly(self):
        return 1  # not allowed


@run_in_both(MyObject)
def test_action_simple():
    """
    True
    True
    hi
    hi
    43
    43
    12
    ? not supposed to return a value
    """
    
    m = MyObject()
    print(m.foo is None)  # None is represented as "null" in JS
    
    m.set_foo("hi")
    print(m.foo is None)
    loop.iter()
    print(m.foo)
    
    m.set_foo(42)
    m.set_foo(43)
    print(m.foo)
    loop.iter()
    print(m.foo)
    
    m.set_foo_add(3, 4, 5)
    print(m.foo)
    loop.iter()
    print(m.foo)
    
    m.do_silly()
    loop.iter()


@run_in_both(MyObject)
def test_action_one_by_one():
    """
    None
    hi
    there
    42
    42
    xx
    bar
    0
    """
    
    m = MyObject()
    print(m.foo)
    
    m.set_foo("hi")
    m.set_foo("there")
    m.set_foo(42)
    
    loop._process_actions(1)  # process one
    print(m.foo)
    loop._process_actions(1)  # process one
    print(m.foo)
    loop._process_actions(1)  # process one
    print(m.foo)
    loop._process_actions(1)  # process one
    print(m.foo)
    
    print('xx')
    
    m.set_foo("foo")
    m.set_foo("bar")
    m.set_foo(0)
    
    loop._process_actions(2)  # process two
    print(m.foo)
    loop._process_actions(2)  # process two
    print(m.foo)


@run_in_both(MyObject)
def test_action_init():
    """
    9
    9
    12
    42
    """
    
    m = MyObject(foo=9)
    print(m.foo)
    loop.iter()
    print(m.foo)
    
    m = MyObject(foo=12)
    print(m.foo)
    m.set_foo(42)
    loop.iter()
    print(m.foo)


class MyObject_autoaction(event.Component):
    
    foo = event.Property(settable=True)


@run_in_both(MyObject_autoaction)
def test_action_auto():
    """
    True
    True
    hi
    """
    
    m = MyObject_autoaction()
    print(m.foo is None)  # None is represented as "null" in JS
    
    m.set_foo("hi")
    print(m.foo is None)
    loop.iter()
    print(m.foo)


class MyObject_actionclash1(event.Component):  # explicit method gets preference
    
    foo = event.Property(settable=True)
    
    @event.action
    def set_foo(self, v):
        print('Custom one')
        self._mutate_foo(v)


class MyObject_actionclash2(MyObject_autoaction):
    
    @event.action
    def set_foo(self, v):
        print('Custom one')
        self._mutate_foo(v)


@run_in_both(MyObject_actionclash1, MyObject_actionclash2)
def test_action_clash():
    """
    Custom one
    hi
    Custom one
    hi
    """
    
    m = MyObject_actionclash1()
    m.set_foo("hi")
    loop.iter()
    print(m.foo)
    
    m = MyObject_actionclash2()
    m.set_foo("hi")
    loop.iter()
    print(m.foo)


class MyObject2(MyObject):
    
    @event.action
    def set_foo(self, v):
        super().set_foo(v + 1)


class MyObject3(MyObject_autoaction):  # base class has autogenerated set_foo
    
    @event.action
    def set_foo(self, v):
        super().set_foo(v + 1)


@run_in_both(MyObject2, MyObject3)
def test_action_inheritance():
    """
    True
    5
    True
    5
    """
    m = MyObject2()
    m.set_foo(4)
    print(m.foo is None)
    loop.iter()
    print(m.foo)  # one iter handles action and supercall in one go
    
    m = MyObject3()
    m.set_foo(4)
    print(m.foo is None)
    loop.iter()
    print(m.foo)


@run_in_both(MyObject)
def test_action_subaction():
    """
    0
    2
    """
    m = MyObject()
    m.set_foo(0)
    loop.iter()
    print(m.foo)
    
    m.increase_foo()
    loop.iter()
    print(m.foo)


class MyObject4(event.Component):
    
    @event.action
    def emitit(self):
        self.emit('boe', dict(value=42))
    
    @event.reaction('!boe')
    def on_boe(self, *events):
        print([ev.value for ev in events])


@run_in_both(MyObject4)
def test_action_can_emit():
    """
    [42]
    [42, 42]
    """
    m = MyObject4()
    
    with loop:
        m.emitit()
    with loop:
        m.emitit()
        m.emitit()


class RecursiveActions(event.Component):
    
    p1 = event.IntProp()
    p2 = event.IntProp()
    
    @event.action
    def set_p1(self, v):
        self.set_p2(v + 1)
        self._mutate_p1(v)
    
    @event.action
    def set_p2(self, v):
        self.set_p1(v - 1)
        self._mutate_p2(v)


@run_in_both(RecursiveActions)
def test_property_recursive():
    """
    0 0
    ? maximum
    0 0
    ? maximum
    0 0
    """
    # What we really test is that we don't do anything to prevent action recursion :)
    m = RecursiveActions()
    loop.iter()
    print(m.p1, m.p2)
    
    try:
        m.set_p1(7)
        loop.iter()
    except Exception as err:
        print(err)
    print(m.p1, m.p2)
    
    try:
        m.set_p2(18)
        loop.iter()
    except Exception as err:
        print(err)
    print(m.p1, m.p2)


## Meta-ish tests that are similar for property/emitter/action/reaction


@run_in_both(MyObject)
def test_action_not_settable():
    """
    fail AttributeError
    """
    
    m = MyObject()
    
    try:
        m.set_foo = 3
    except AttributeError:
        print('fail AttributeError')
    
    # We cannot prevent deletion in JS, otherwise we cannot overload


def test_action_python_only():
    
    m = MyObject()
    
    # Action decorator needs proper callable
    with raises(TypeError):
        event.action(3)
    with raises(TypeError):
        event.action(isinstance)
    
    # Check type of the instance attribute
    assert isinstance(m.set_foo, event._action.Action)
    
    # Cannot set or delete an action
    with raises(AttributeError):
        m.set_foo = 3
    with raises(AttributeError):
        del m.set_foo
    
    # Repr and docs
    assert 'action' in repr(m.__class__.set_foo).lower()
    assert 'action' in repr(m.set_foo).lower()
    assert 'foo' in repr(m.set_foo)
    # Also for autogenereated action
    m = MyObject_autoaction()
    assert 'action' in repr(m.__class__.set_foo).lower()
    assert 'action' in repr(m.set_foo).lower()
    assert 'foo' in repr(m.set_foo)


run_tests_if_main()
