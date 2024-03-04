from pydantic import BaseModel
from typing import Optional

class ReportPayload(BaseModel):
    name: str
    version: str
    rules_matched: list[str]
    inspector_url: str
    additional_information: Optional[str] = None
    recipient: Optional[str] = None
