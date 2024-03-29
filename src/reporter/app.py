import logging
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from msgraph import GraphServiceClient
from reporter.schemas import ReportPayload
from reporter.constants import Mail
import sentry_sdk

from reporter.constants import GIT_SHA, Sentry
from reporter.pypi_client import ObservationsAPIFailure, PyPIClientDependency
from reporter.models import Observation, ServerMetadata, EchoResponse

from reporter.dependencies import build_graph_client
from reporter.mailer import build_report_email_content, send_mail

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
    return ServerMetadata(
        commit=GIT_SHA,
    )


@app.get("/echo", summary="Echo the username of the PyPI User")
async def echo(pypi_client: PyPIClientDependency) -> EchoResponse:
    """Return the username of the PyPI User."""
    username = await pypi_client.echo()
    return EchoResponse(username=username)


@app.post("/report/{project_name}")
async def report_endpoint(project_name: str, observation: Observation, pypi_client: PyPIClientDependency):
    try:
        await pypi_client.send_observation(project_name=project_name, observation=observation)
    except ObservationsAPIFailure as exc:
        sentry_sdk.capture_exception(exc)
        log.error(f"PyPI Observations API failed with response code {exc.response.status_code}: {exc.response.text}")
        raise HTTPException(400, detail="PyPI Observations API failed")


@app.post("/report/email")
async def report_email_endpoint(
    payload: ReportPayload, graph_client: Annotated[GraphServiceClient, Depends(build_graph_client)]
):
    content = build_report_email_content(
        name=payload.name,
        version=payload.version,
        inspector_url=payload.inspector_url,
        rules_matched=payload.rules_matched,
        additional_information=payload.additional_information,
    )
    await send_mail(
        graph_client,
        to_addresses=[payload.recipient or Mail.recipient],
        bcc_addresses=[],
        subject=f"Automated PyPI Malware Report: {payload.name}@{payload.version}",
        content=content,
    )
