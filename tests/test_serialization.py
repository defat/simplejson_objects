import pytest
import logging

from simplejson_objects import *

logging.basicConfig(level=logging.DEBUG)


def test_basic_types_serialization():
    assert loads(dumps(None)) is None
    assert loads(dumps([])) == []
    assert loads(dumps({})) == {}

    assert loads(dumps([1, 1.2, 'string'])) == [1, 1.2, 'string']
    assert loads(dumps({'string': 1})) == {'string': 1}


def test_raises_on_objects():
    class A:
        pass
    with pytest.raises(TypeError):
        dumps(A())


def test_datetime():
    dt = datetime.fromtimestamp(1234)
    dict_ = json.loads(dumps(dt))
    assert dict_[TYPE_ATTR] == datetime.__name__
    assert dict_[TIMESTAMP_ATTR] == dt.timestamp()
    assert loads(dumps(dt)) == dt


@pytest.fixture
def class_A():
    class A(SerializableMixin):
        def __init__(self, a):
            self.a = a
            self._a = a
    return A


def test_objects_serialization_check_type_attr(class_A):
    a = class_A(1)
    assert eval(dumps(a))[TYPE_ATTR] == type(a).__module__ + '.A'


def test_objects_serialization(class_A):
    a = class_A(1)
    assert loads(dumps(a)).a == 1

    a = class_A([1, 2, 3])
    assert loads(dumps(a)).a == [1, 2, 3]


def test_objects_does_not_have_underscored_attrs(class_A):
    a = class_A(1)
    assert not hasattr(loads(dumps(a)), '_a')


def test_recursive(class_A):
    a = class_A(class_A(1))
    assert loads(dumps(a)).a.a == 1


def test_mixin():
    class A(SerializableMixin):
        def __init__(self):
            self.unused = 1

        def _get_data(self):
            return {'a': 1}

    a = A()
    a = loads(dumps(a))

    assert a.a == 1
    assert not hasattr(a, 'unused')


def test_mixin_dumps_loads():
    class A(SerializableMixin):
        def __init__(self, a):
            self.a = a

    a = A(1)
    a = A.loads(a.dumps())

    assert a.a == 1


def test_transitiveness(class_A):
    a = class_A(1)

    a_new = loads(dumps(loads(dumps(a))))
    assert a_new.a == a.a
