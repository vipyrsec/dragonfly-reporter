"""Models and types."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, model_validator


class ServerMetadata(BaseModel):
    """Server metadata."""

    commit: str


class EchoResponse(BaseModel):
    """Response from PyPI's echo endpoint."""

    username: str


# Taken from
# https://github.com/pypi/warehouse/blob/4d2628560e6e764dc80a026fa080e9cf70446c81/warehouse/observations/models.py#L109-L122
class ObservationKind(Enum):
    """The kinds of observations we can make."""

    DependencyConfusion = "is_dependency_confusion"
    Malware = "is_malware"
    Spam = "is_spam"
    Other = "something_else"


class Observation(BaseModel):
    """An observation to report about a package.

    Attributes:
        kind: The kind of the observation.
        summary: A summary of the observation.
        inspector_url: The PyPI inspector URL for the observation.
        extra: Any extra information to add to the observation.
    """

    kind: ObservationKind
    summary: str
    inspector_url: str | None
    extra: dict[str, Any] = {}

    @model_validator(mode="after")
    def model_validator(self: Observation) -> Observation:
        """Validate the observation to ensure reports are complete."""
        if self.kind == ObservationKind.Malware:
            assert self.inspector_url is not None, "inspector_url is required when kind is malware"

        return self
