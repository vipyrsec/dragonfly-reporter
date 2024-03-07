from typing import Annotated
from fastapi import Depends, FastAPI
from msgraph import GraphServiceClient
from reporter.schemas import ReportPayload
from reporter.constants import Mail
import sentry_sdk

from reporter.constants import GIT_SHA, Sentry
from reporter.pypi_client import PyPIClientDependency
from reporter.models import Observation, ServerMetadata

from reporter.dependencies import build_graph_client
from reporter.mailer import build_report_email_content, send_mail

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
async def echo(pypi_client: PyPIClientDependency) -> str:
    """Return the username of the PyPI User."""
    return await pypi_client.echo()


@app.post("/report/{project_name}")
async def report_endpoint(project_name: str, observation: Observation, pypi_client: PyPIClientDependency):
    await pypi_client.send_observation(project_name=project_name, observation=observation)


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
