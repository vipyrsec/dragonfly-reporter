from pydantic import BaseModel


class ReportPayload(BaseModel):
    name: str
    version: str
    rules_matched: list[str]
    inspector_url: str
    additional_information: str | None = None
    recipient: str | None = None
