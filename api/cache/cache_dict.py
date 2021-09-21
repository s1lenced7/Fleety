from datetime import datetime
from copy import deepcopy

MAX_SIZE = 2000
MAX_AGE = 60 * 60  # 1 hour
MAX_SIZE_TRIM = MAX_SIZE / 4


class CacheEntry:

    def __init__(self, value):
        self.last_accessed = datetime.utcnow()
        self._value = deepcopy(value)

    @property
    def value(self):
        self.last_accessed = datetime.utcnow()
        return deepcopy(self._value)

    @property
    def age(self):
        return (datetime.utcnow() - self.last_accessed).seconds


class CacheDict(dict):
    """
        Not that efficient but hey ¯\_(ツ)_/¯
    """

    def __init__(self, *args, max_size=MAX_SIZE, max_age=MAX_AGE, max_size_trim=MAX_SIZE_TRIM, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_age = max_age
        self._max_size = max_size
        self._max_size_trim = max_size_trim

    def _evict(self):
        evicted_keys = set()
        for key, value in self.items():
            if value.age >= self._max_age:
                evicted_keys.add(key)

        if len(self) - len(evicted_keys) >= self._max_size:
            evicted_key_count = 0
            for key, value in sorted(self.items(), key=lambda v: v[1].age, reverse=True):
                if evicted_key_count >= self._max_size_trim:
                    break
                if key not in evicted_keys:
                    evicted_keys.add(key)
                    evicted_key_count += 1

        for key in evicted_keys:
            self.__delitem__(key)

    def get(self, k):
        cache_entry = super().get(k)
        if cache_entry:
            return cache_entry.value
        return cache_entry

    def __getitem__(self, key):
        item = super().__getitem__(key)
        self._evict()
        return item.value

    def __setitem__(self, key, value):
        super().__setitem__(key, CacheEntry(value))



