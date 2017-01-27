from collections import namedtuple
from functools import partial
from datetime import datetime

try:
    import simplejson as json
except ImportError:
    import json


TYPE_ATTR = '__type__'
TIMESTAMP_ATTR = 'timestamp'


def _datetime_asdict(obj):
    return {
        TYPE_ATTR: datetime.__name__,
        TIMESTAMP_ATTR: obj.timestamp()
    }


def _datetime_fromdict(dict_):
    return datetime.fromtimestamp(dict_[TIMESTAMP_ATTR])


def _default(obj):
    if isinstance(obj, datetime):
        return _datetime_asdict(obj)
    if hasattr(obj, '_asdict'):
        return obj._asdict()
    raise TypeError(repr(obj) + " is not JSON serializable")


def _object_hook(json_object):
    if TYPE_ATTR in json_object:
        type_name = json_object.pop(TYPE_ATTR)
        if type_name == datetime.__name__:
            return _datetime_fromdict(json_object)
        type_ = namedtuple(type_name, json_object.keys())
        return type_(**json_object)
    return json_object


class SerializableMixin:
    def _get_data(self) -> {}:
        """
        Override this in subclasses if needed. Should return dictionary representing object's state
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def _asdict(self):
        dict_ = self._get_data()
        dict_[TYPE_ATTR] = type(self).__name__
        return dict_

    @classmethod
    def loads(cls, json_data: str):
        """
        Passes all attributes from json dictionary to __init__ method
        :param json_data
        """
        res = loads(json_data)
        assert res.__class__.__name__ == cls.__name__
        return cls(**res.__dict__)

    def dumps(self):
        return dumps(self)


dumps = partial(json.dumps, default=_default)
loads = partial(json.loads, object_hook=_object_hook)

register_args = (dumps, loads, 'application/json', 'utf-8')
