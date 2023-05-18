import os
from pydantic import AnyUrl, BaseSettings, Field


class MoDSWrapperSettings(BaseSettings):
    agent_base_url: AnyUrl = Field(
        os.environ.get("MODS_AGENT_BASE_URL", default="http://localhost:5000/"), description="")

    poll_intervall: int = Field(
        int(os.environ.get("POLLING_INTERVAL", default="10")), description="Polling interval when waiting or jobs to finish (seconds)"
    )

    max_attemps: int = Field(
        int(os.environ.get("MAX_ATTEMPTS", default="60")), description="Maximum number of requests when waiting for jobs to finish"
    )

    submission_url_part: str = Field(
        "/request?query=", description="Additional URL part for job submission"
    )

    output_url_part: str = Field(
        "/output/request?query=",
        description="Additional URL part for requesting job output",
    )

    class Config:
        env_prefix = "MODS_"
