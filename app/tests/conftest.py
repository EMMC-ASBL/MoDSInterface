"""Pytest fixtures for `strategies/`."""
import os
from typing import Any, Dict

import pytest

DIRNAME = os.path.dirname(__file__)


@pytest.fixture(scope="session")
def celery_config() -> Dict[Any, Any]:
    from app.models import AppConfig

    settings = AppConfig()

    return {
        "broker_url": settings.get_redis_address(),
        "result_backend": settings.get_redis_address(),
    }


@pytest.fixture(scope="session")
def celery_includes():
    return [
        "app.tasks",
    ]


@pytest.fixture(scope="session")
def celery_enable_logging() -> bool:
    return True
