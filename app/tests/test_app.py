import os
import time
from typing import TYPE_CHECKING

import pytest

DIRNAME = os.path.dirname(__file__)
SCHEMA_FILE_INPUT = os.path.join(DIRNAME, "schema_input.yml")
SCHEMA_FILE_OUTPUT = os.path.join(DIRNAME, "schema_output.yml")


def try_get_redis():
    import os

    import redis

    r = redis.Redis(
        host=os.getenv("MODS_APP4_REDIS_HOST"), port=os.getenv("MODS_APP4_REDIS_PORT")
    )
    try:
        is_available = r.ping()
    except Exception:
        is_available = False

    return not is_available


@pytest.fixture(scope="module")
def module_client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as testclient:
        yield testclient


@pytest.fixture(scope="module")
def get_content():
    filename = "inputs.json"
    path = os.path.join(DIRNAME, filename)
    with open(path, "r+") as file:
        content = file.read()
    return content


@pytest.mark.usefixtures("module_client")
@pytest.mark.usefixtures("celery_app")
@pytest.mark.usefixtures("celery_worker")
@pytest.mark.skipif(try_get_redis(), reason="Redis host is not available")
def test_app(module_client, celery_app, celery_worker, get_content) -> None:
    import json
    from io import StringIO

    from osp.core.namespaces import amiii
    from osp.core.utils import import_cuds
    from osp.core.utils.schema_validation import validate_tree_against_schema

    import osp.ontology as opath

    response = module_client.get("/docs")
    assert response.status_code == 200

    response = module_client.post(
        f"run/", data=get_content, headers={"Content-Type": "application/ld+json"}
    )

    assert response.status_code == 200

    time.sleep(15)

    uuid = response.json().get("task_id")

    response = module_client.get(f"status/{uuid}")

    assert response.status_code == 200
    assert response.json().get("status") == "SUCCESS"

    response = module_client.get(f"get/{uuid}")

    assert response.status_code == 200
    cuds = import_cuds(StringIO(response.text), format="turtle")
    root = [obj for obj in cuds if obj.is_a(amiii.beamManufacturingDatum)]
    assert [] != root
    assert len(root) == 2
    for obj in root:
        validate_tree_against_schema(obj, SCHEMA_FILE_OUTPUT)

    response = module_client.get(f"/example")

    assert response.status_code == 200

    cuds = import_cuds(StringIO(response.text), format="text/turtle")
    root = [obj for obj in cuds if obj.is_a(amiii.beamManufacturingDatum)]
    assert [] != root
    assert len(root) == 2
    for obj in root:
        validate_tree_against_schema(obj, SCHEMA_FILE_INPUT)

    response = module_client.get(f"/example_collection")
    coll_path = os.path.join(*opath.__path__, "collection_inputs.json")
    with open(coll_path, "r") as file:
        content = json.loads(file.read())
    assert response.json() == content
