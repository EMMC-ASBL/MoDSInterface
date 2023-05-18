import logging
from io import BufferedReader
from diskcache import Cache

logger = logging.getLogger(__name__)


def read_cache_as_string(cache_key, cache_directory, cache_size_limit) -> str:
    with Cache(cache_directory, size_limit=cache_size_limit) as cache:
        cache_inst = cache.read(cache_key)
        if isinstance(cache_inst, BufferedReader):
            return cache_inst.read().decode()
        elif isinstance(cache_inst, bytes):
            return cache_inst.decode()
        elif isinstance(cache_inst, str):
            return cache_inst
        else:
            logger.error(
                "%s is of type %s is not one of string, bytes, or buffered reader.",
                cache_inst,
                type(cache_inst),
            )
            raise TypeError(
                f"{cache_inst} is of type {type(cache_inst)} is not one of string, bytes, or buffered reader."
            )
