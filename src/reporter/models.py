from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, model_validator


class ServerMetadata(BaseModel):
    """Server metadata."""

    commit: str


# Taken from
# https://github.com/pypi/warehouse/blob/4d2628560e6e764dc80a026fa080e9cf70446c81/warehouse/observations/models.py#L109-L122
class ObservationKind(Enum):
    DependencyConfusion = "is_dependency_confusion"
    Malware = "is_malware"
    Spam = "is_spam"
    Other = "something_else"


class Observation(BaseModel):
    kind: ObservationKind
    summary: str
    inspector_url: Optional[str]
    extra: dict[str, Any] = {}

    @model_validator(mode="after")
    def model_validator(self: Observation) -> Observation:
        if self.kind == ObservationKind.Malware:
            assert self.inspector_url is not None, "inspector_url is required when kind is malware"

        return self
