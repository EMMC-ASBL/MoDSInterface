"""Pytest fixtures for `strategies/`."""
from typing import Any, Dict

import pytest


@pytest.fixture(scope="session")
def celery_config() -> Dict[Any, Any]:
    from app.models import AppConfig

    settings = AppConfig()

    return {
        "broker_url": settings.get_redis_address(),
        "result_backend": settings.get_redis_address(),
    }


def test_worker_initializes(celery_worker):
    assert True


@pytest.fixture(scope="session")
def celery_includes():
    return [
        "app.tasks",
    ]


@pytest.fixture(scope="session")
def celery_enable_logging() -> bool:
    return True
