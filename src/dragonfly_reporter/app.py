from fastapi import FastAPI

from dragonfly_reporter.http_client import http_client

app = FastAPI()

@app.get("/")
async def echo() -> str:
    """Return the username of the PyPI User."""
    response = await http_client.get("/echo")
    return response.text
