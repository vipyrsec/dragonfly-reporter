from fastapi import FastAPI

from .report import echo

app = FastAPI()


@app.get("/")
async def root():
    return await echo()
