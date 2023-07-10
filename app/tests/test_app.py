import os
from io import StringIO
import time
import pytest
import redis
from osp.core.namespaces import mods
from osp.core.utils import import_cuds
from osp.core.utils.schema_validation import validate_tree_against_schema

DIRNAME = os.path.dirname(__file__)
SCHEMA_FILE_INPUT = os.path.join(DIRNAME, "schema_input.yml")
SCHEMA_FILE_OUTPUT = os.path.join(DIRNAME, "schema_output.yml")


def try_get_redis():
    host = os.getenv("MODS_REDIS_HOST")
    assert host is not None

    port_string = os.getenv("MODS_REDIS_PORT")
    assert port_string is not None

    redis_bytes = redis.Redis(host=host, port=int(port_string))
    try:
        is_available = redis_bytes.ping()
    except Exception:
        is_available = False

    return not is_available


def get_content(jsonfile):
    path = os.path.join(DIRNAME, jsonfile)
    with open(path, "r+") as file:
        content = file.read()
    return content


@pytest.fixture(scope="module")
def module_client():
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as testclient:
        yield testclient


@pytest.mark.usefixtures("module_client")
@pytest.mark.parametrize("jsonfile", ["input.json"])
@pytest.mark.skipif(try_get_redis(), reason="Redis host is not available")
def test_app_run(module_client, jsonfile) -> None:
    response = module_client.get("/docs")
    assert response.status_code == 200
    print("docs: ", response.text)

    response = module_client.post(
        "run/",
        data=get_content(jsonfile),
        headers={"Content-Type": "application/ld+json"},
    )

    print("run: ", response.text)

    assert response.status_code == 200

    time.sleep(15)

    uuid = response.json().get("task_id")

    response = module_client.get(f"status/{uuid}")

    assert response.status_code == 200
    assert response.json().get("status") == "SUCCESS"

    response = module_client.get(f"get/{uuid}")

    assert response.status_code == 200
    cuds = import_cuds(StringIO(response.text), format="turtle")
    root = [obj for obj in cuds if obj.is_a(mods.MultiObjectiveSimulation)]
    assert [] != root
    assert len(root) == 1
    for obj in root:
        validate_tree_against_schema(obj, SCHEMA_FILE_OUTPUT)


@pytest.mark.usefixtures("module_client")
@pytest.mark.skipif(try_get_redis(), reason="Redis host is not available")
def test_app_get(module_client) -> None:
    response = module_client.get("/examples/simphony/turtle")
    print(response.text)
    assert response.status_code == 200

    cuds = import_cuds(StringIO(response.text), format="text/turtle")

    if isinstance(cuds, list):
        root = [obj for obj in cuds if obj.is_a(mods.MultiObjectiveSimulation)]
        assert len(root) == 1
    else:
        assert cuds.oclass == mods.MultiObjectiveSimulation
        root = [cuds]

    for obj in root:
        validate_tree_against_schema(obj, SCHEMA_FILE_INPUT)
