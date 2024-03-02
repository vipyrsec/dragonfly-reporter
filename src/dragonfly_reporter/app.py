from fastapi import FastAPI

from dragonfly_reporter.http_client import HTTPClientDependency
from dragonfly_reporter.models import Observation
from dragonfly_reporter.observations import send_observation

app = FastAPI()

@app.get("/")
async def echo(http_client: HTTPClientDependency) -> str:
    """Return the username of the PyPI User."""
    response = await http_client.get("/echo")
    return response.text

@app.post("/report/{project_name}")
async def report_endpoint(project_name: str, observation: Observation, http_client: HTTPClientDependency):
    await send_observation(project_name=project_name, observation=observation, http_client=http_client)
