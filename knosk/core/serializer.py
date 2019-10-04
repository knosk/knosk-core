from datetime import datetime, time, date
from dateutil.parser import parse
import importlib


def __model_serializer(value):
    if isinstance(value, datetime) or isinstance(value, time) or isinstance(value, date):
        return {"obj": type(value).__name__, "value": str(value)}
    elif isinstance(value, tuple):
        return {"tuple": [__model_serializer(v) for v in value]}
    else:
        return value


def __model_deserializer(value):
    if value and isinstance(
        value,
        dict) and "obj" in value and value["obj"] not in [
        'time',
        'datetime',
            'date']:
        module_name, class_name = value["obj"].rsplit(".", 1)
        model_cls = getattr(importlib.import_module(module_name), class_name)
        return model_cls.objects.get(id=value["id"])
    elif value and isinstance(value, dict) and "obj" in value:
        result = parse(value['value'])
        if value["obj"] == 'time':
            result = result.time()
        if value["obj"] == 'date':
            result = result.date()
        return result
    elif value and isinstance(value, dict) and "tuple" in value:
        return tuple([__model_deserializer(v) for v in value['tuple']])
    else:
        return value


def __simple_handler(value, action):
    if isinstance(value, list):
        return [action(v) for v in value]
    else:
        return action(value)


def __handler(data, action):
    res = {}
    for name, value in data.items():
        res[name] = __simple_handler(value, action)
    return res


def serialize(data):
    return __handler(data, __model_serializer)


def simple_serialize(data):
    return __simple_handler(data, __model_serializer)


def deserialize(data):
    return __handler(data, __model_deserializer)


def simple_deserialize(data):
    return __simple_handler(data, __model_deserializer)
