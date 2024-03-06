from fastapi import FastAPI
import sentry_sdk

from reporter.constants import GIT_SHA, Sentry
from reporter.http_client import HTTPClientDependency
from reporter.models import Observation, ServerMetadata
from reporter.observations import send_observation

sentry_sdk.init(
    dsn=Sentry.dsn,
    environment=Sentry.environment,
    send_default_pii=True,
    traces_sample_rate=0.05,
    profiles_sample_rate=0.05,
    release=f"{Sentry.release_prefix}@{GIT_SHA}",
)

app = FastAPI()


@app.get("/", summary="Get the server's metadata")
async def metadata() -> ServerMetadata:
    """Get server metadata."""
    return ServerMetadata(
        commit=GIT_SHA,
    )


@app.post("/report/{project_name}")
async def report_endpoint(project_name: str, observation: Observation, http_client: HTTPClientDependency):
    await send_observation(project_name=project_name, observation=observation, http_client=http_client)
