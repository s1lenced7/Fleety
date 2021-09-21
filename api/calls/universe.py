from api.cache import API_CACHES, args_kwargs_to_cache_key
from .base import CachedSwaggerAPICall
from data_structures.general.universe import UniverseItem


class UniverseItemsFromID(CachedSwaggerAPICall):
    route = 'universe/names/'
    response_type = UniverseItem

    @classmethod
    def _get(cls, ids):
        return cls._execute(json_body=ids)

    @classmethod
    def _to_data_structure(cls, json_obj, id=None):
        return [super(UniverseItemsFromID, cls)._to_data_structure(obj) for obj in json_obj]

    @classmethod
    def get(cls, *args, **kwargs):
        ids = []
        results = []
        missing_ids = []
        cache = API_CACHES[cls]
        for arg in args:
            if isinstance(arg, list):
                ids += arg
            else:
                ids.append(arg)

        for id in ids:
            cached_result = cache.get(id)
            if cached_result:
                results.append(cached_result)
            else:
                missing_ids.append(id)

        if missing_ids:
            api_results = cls._get(missing_ids)
            for result in api_results:
                cache[result.id] = result
            results += api_results

        return results

