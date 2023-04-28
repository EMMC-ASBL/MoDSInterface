import logging
from importlib import import_module
from io import StringIO
from typing import TYPE_CHECKING
from uuid import uuid4

from celery import Celery, Task, signals
from diskcache import Cache
from osp.core.namespaces import cuba
from osp.core.utils import export_cuds, import_cuds

from .models import AppConfig

if TYPE_CHECKING:
    from typing import Any, Callable, Dict


def get_wrapper_class(module: str) -> "Callable":
    module, classname = module.strip().split(":")
    return getattr(import_module(module), classname)


settings = AppConfig()
address = settings.get_redis_address()
celery = Celery(broker=address, backend=address)
celery.conf.CELERYD_HIJACK_ROOT_LOGGER = False


@signals.setup_logging.connect
def on_setup_logging(**kwargs):
    # Get the root logger
    logger = logging.getLogger()

    # Set the logging level to INFO
    logger.setLevel(logging.INFO)

    # Add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


@celery.task
def run_simulation(cache_key: str) -> str:

    with Cache(settings.cache_directory, size_limit=settings.cache_size_limit) as cache:
        content = StringIO(cache.read(cache_key).decode())

    session_class = get_wrapper_class(settings.wrapper_name)
    with session_class() as session:
        wrapper = cuba.Wrapper(session=session)
        cuds = import_cuds(content, session=session)
        wrapper.add(*cuds, rel=cuba.relationship)
        session.run()

    result_key = str(uuid4)

    with Cache(settings.cache_directory, size_limit=settings.cache_size_limit) as cache:
        cuds = StringIO()
        export_cuds(session, cuds)
        cuds.seek(0)
        seralized = cuds.read()
        cache.set(
            result_key,
            seralized.encode(),
            read=True,
            expire=settings.cache_expire,
            tag="meta",
        )

    return result_key
