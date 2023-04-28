import os
import tempfile
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union
from uuid import UUID

from fastapi_plugins import RedisSettings
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from typing import Any, Dict, List


DEFAULT_CACHE = os.path.join(tempfile.gettempdir(), "ospcache")


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class Status(BaseModel):
    message: str = Field(...,
                         description="Message when successfully launched wrapper.")
    status: TaskStatus = Field(..., description="Status of the remote task.")
    state: TaskStatus = Field(..., description="State of the remote task.")
    task_id: UUID = Field(..., description="UUID of the submitted task.")
    result: Optional[Any] = Field(
        ..., description="Result of the task forwarded by celery-worker."
    )
    args: Optional[Union[Any, "List[Any]"]] = Field(
        ..., description="Arguments passed during the task submission."
    )
    kwargs: Optional[Union[Any, "List[Any]"]] = Field(
        ..., description="Keyword arguments passed during the task submission."
    )
    traceback: Optional[str] = Field(
        ..., description="Traceback message about potential errors."
    )
    date_done: Union[datetime, Any] = Field(
        ..., description="Datetime when the submitted job finished."
    )


class AppConfig(RedisSettings):
    """Main configuration for FastAPI-middleware based on redis-settings"""

    authentication_dependencies: Optional[str] = Field(
        None,
        description="""FastAPI-authentication dependencies. 
        Should be in the pattern: 
        `my_package.my_module:MyClass | my_other_package.my_other_module:MyOtherClass`.
         """,
    )
    ontology_file: str = Field(
        "mods.ttl", description="File path of the t-box ontology to be shared."
    )
    cuds_turtle_file: str = Field(
        "mods-cmcl-moo-input.ttl",
        description="File path of an a-box turtle file to be shared as example input.",
    )
    cuds_json_file: str = Field(
        "mods-cmcl-moo-input.json",
        description="File path of an a-box json file to be shared as example input.",
    )

    wrapper_name: str = Field(
        "osp.wrappers.sim_cmcl_mods_wrapper.mods_session:MoDS_Session",
        description="""SimWrapperSession class to be loaded from a python module. 
        The regex is: mypackage.mymodule:MyClass""",
    )
    cache_size_limit: int = Field(
        2 * (2**30), description="Size limit per file in the cache"
    )
    cache_directory: Path = Field(
        DEFAULT_CACHE, description="Directory for writing the disk cache."
    )

    cache_expire: int = Field(
        60 * 60 * 24 * 14,
        description="Expiration time of a file in seconds. Default is two weeks.",
    )

    class Config:
        env_prefix = "MODS_"
