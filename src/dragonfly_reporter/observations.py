from __future__ import annotations

import httpx
from fastapi.encoders import jsonable_encoder

from dragonfly_reporter.models import Observation


async def send_observation(
    project_name: str, observation: Observation, *, http_client: httpx.AsyncClient
):
    url = f"/danger-api/projects/{project_name}/observations"
    json = jsonable_encoder(observation)

    await http_client.post(url, json=json)
