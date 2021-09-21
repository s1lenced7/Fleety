from collections import defaultdict
from .cache_dict import CacheDict

API_CACHES = defaultdict(CacheDict)


def dict_to_cache_key(d: dict):
    key = '{'
    dict_keys = sorted(d.keys(), key=lambda v: str(v))
    for dict_key in dict_keys:
        value = dict[dict_key]
        if isinstance(value, dict):
            key += f'{dict_key}={dict_to_cache_key(value)}'
        elif isinstance(value, list):
            key += f'{dict_key}={list_to_cache_key(value)}'
        else:
            key += f'{dict_key}={value}'
        key += '|'
    key += '}'
    return key


def list_to_cache_key(l):
    key = '['
    for i in l:
        if isinstance(i, dict):
            key += dict_to_cache_key(i)
        elif isinstance(i, list):
            key += f'{list_to_cache_key(i)}'
        else:
            key += str(i)
        key += '&'
    key += ']'
    return key


def args_kwargs_to_cache_key(*args, **kwargs):
    key = list_to_cache_key(args)
    key += dict_to_cache_key(kwargs)
    return key
