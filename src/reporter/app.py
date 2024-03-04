from typing import Annotated
from fastapi import Depends, FastAPI
from msgraph import GraphServiceClient
from reporter.schemas import ReportPayload
from reporter.constants import Mail
from reporter.http_client import HTTPClientDependency
from reporter.models import Observation
from reporter.observations import send_observation

from reporter.dependencies import build_graph_client
from reporter.mailer import build_report_email_content, send_mail

app = FastAPI()


@app.get("/")
async def echo(http_client: HTTPClientDependency) -> str:
    """Return the username of the PyPI User."""
    response = await http_client.get("/echo")
    return response.text


@app.post("/report/{project_name}")
async def report_endpoint(project_name: str, observation: Observation, http_client: HTTPClientDependency):
    await send_observation(project_name=project_name, observation=observation, http_client=http_client)


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
