"""The application server."""

import logging

import sentry_sdk
from fastapi import FastAPI, HTTPException

from reporter.constants import GIT_SHA, Sentry
from reporter.models import EchoResponse, Observation, ServerMetadata
from reporter.pypi_client import ObservationsAPIFailure, PyPIClientDependency

log = logging.getLogger(__name__)

sentry_sdk.init(
    dsn=Sentry.dsn,
    environment=Sentry.environment,
    send_default_pii=True,
    traces_sample_rate=0.05,
    profiles_sample_rate=0.05,
    release=f"{Sentry.release_prefix}@{GIT_SHA}",
)

app = FastAPI()


@app.get("/", summary="Get server metadata")
async def metadata() -> ServerMetadata:
    """Get server metadata."""
    return ServerMetadata(commit=GIT_SHA)


@app.get("/echo", summary="Echo the username of the PyPI User")
async def echo(pypi_client: PyPIClientDependency) -> EchoResponse:
    """Return the username of the PyPI User."""
    username = await pypi_client.echo()
    return EchoResponse(username=username)


@app.post("/report/{project_name}")
async def report(project_name: str, observation: Observation, pypi_client: PyPIClientDependency) -> None:
    """Report an observation for the project.

    Args:
        project_name: The name of the PyPI project to report.
        observation: The observation to report.
        pypi_client: The PyPI API client used to report.

    Raises:
        HTTPException: In case of PyPI API errors.
    """
    try:
        await pypi_client.send_observation(project_name=project_name, observation=observation)
    except ObservationsAPIFailure as exc:
        log.exception(
            "PyPI Observations API failed with response code %d: %s",
            exc.response.status_code,
            exc.response.text,
        )
        sentry_sdk.capture_exception(exc)

        raise HTTPException(400, detail="PyPI Observations API failed") from exc
