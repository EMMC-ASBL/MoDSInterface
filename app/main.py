import logging
import os
from importlib import import_module
from typing import TYPE_CHECKING, Callable, List, Optional
from uuid import uuid4

from celery import Celery
from diskcache import Cache
from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response
from fastapi_plugins import (config_plugin, depends_config, get_config,
                             redis_plugin, register_config,
                             register_middleware)
from pydantic import BaseSettings

import osp.ontology as opath

from .models import AppConfig, Status

MIME_TYPES = ["text/turtle", "application/ld+json"]


if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, Dict, List


logger = logging.getLogger(__name__)


def get_file(
    filename: str, failure_message: str, media_type: str = "application/json"
) -> Response:
    path = os.path.join(*opath.__path__, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=failure_message)
    with open(path, "r") as file:
        content = file.read()
    return Response(content=content, media_type=media_type)


def get_deps() -> "List[Depends]":
    settings = AppConfig()
    if settings.authentication_dependencies:
        modules = [
            module.strip().split(":")
            for module in settings.authentication_dependencies.split("|")
        ]
        mods = [
            (module, classname.replace("()", ""), True)
            if "()" in classname
            else (module, classname, False)
            for (module, classname) in modules
        ]
        imports = [
            (getattr(import_module(module), classname), called)
            for (module, classname, called) in mods
        ]
        dependencies = [
            Depends(dependency()) if called else Depends(dependency)
            for (dependency, called) in imports
        ]
        logger.info(
            "Imported the following dependencies for authentication: %s", dependencies
        )
    else:
        dependencies = []
        logger.info("No dependencies for authentication assigned.")
    return dependencies


async def get_body(request: Request = Body(..., media_type="text/turtle")) -> str:
    content_type = request.headers.get("Content-Type")
    if content_type not in MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Payload must be one of the following types: {MIME_TYPES}",
        )
    return await request.body()


def get_app() -> Celery:
    from .tasks import celery

    return celery


def get_method() -> Callable:
    from .tasks import run_simulation

    return run_simulation


app = register_middleware(FastAPI(dependencies=get_deps()))
register_config(AppConfig)
config = get_config()


@app.post("/run/")
async def run_task(
    content: bytes = Depends(get_body),
    method: Callable = Depends(get_method),
    settings: BaseSettings = Depends(depends_config),
) -> Status:
    key = str(uuid4())
    with Cache(settings.cache_directory, size_limit=settings.cache_size_limit) as cache:
        cache.set(
            key,
            content,
            read=True,
            expire=settings.cache_expire,
        )
    task = method.delay(key)
    return Status(
        message="Task submitted.",
        status=task.status,
        result=task.result,
        state=task.state,
        traceback=task.traceback,
        task_id=task.id,
        args=task.args,
        kwargs=task.kwargs,
        date_done=task.date_done,
    )


@app.get("/status/{task_id}")
def status(task_id: str, celery: Celery = Depends(get_app)) -> Status:
    task = celery.AsyncResult(task_id)
    return Status(
        message="Status of task was fetched.",
        status=task.status,
        result=task.result,
        state=task.state,
        traceback=task.traceback,
        task_id=task.id,
        args=task.args,
        kwargs=task.kwargs,
        date_done=task.date_done,
    )


@app.get("/get/{task_id}")
def status(
    task_id: str,
    celery: Celery = Depends(get_app),
    settings: "BaseSettings" = Depends(depends_config),
) -> Response:
    result = celery.AsyncResult(task_id)
    if not result.ready():
        raise HTTPException(status_code=400, detail="Task is not ready yet.")
    with Cache(settings.cache_directory, size_limit=settings.cache_size_limit) as cache:
        content = cache.read(result.result)
    return Response(content=content, media_type="text/turtle")


@app.get("/ontology")
def get_ontology(settings: "BaseSettings" = Depends(depends_config)) -> Response:
    ontology_path = os.path.join(*opath.__path__, settings.ontology_file)
    if not os.path.exists(ontology_path):
        raise HTTPException(
            status_code=404, detail="Ontology file is not available")
    with open(ontology_path, "r") as file:
        content = file.read()
    return Response(content=content, media_type="text/turtle")


@app.get("/examples/simphony/turtle")
def get_turtle_example(settings: "BaseSettings" = Depends(depends_config)) -> Response:
    logger.info("Getting example turtle file...")
    return get_file(
        settings.cuds_turtle_file,
        "Example a-box turtle file is not available",
        media_type="text/turtle",
    )


@app.get("/examples/simphony/json")
def get_json_example(settings: "BaseSettings" = Depends(depends_config)) -> Response:
    logger.info("Getting example json file...")
    return get_file(
        settings.cuds_json_file,
        "Example a-box json file is not available",
        media_type="text/json",
    )


@app.on_event("startup")
async def on_startup() -> None:
    """Define functions for app during startup"""
    await config_plugin.init_app(app, config)
    await config_plugin.init()
    await redis_plugin.init_app(app, config=config)
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Define functions for app during shutdown"""
    await redis_plugin.terminate()
    await config_plugin.terminate()
