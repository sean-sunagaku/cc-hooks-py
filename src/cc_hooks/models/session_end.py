from typing import Literal

from pydantic import Field

from cc_hooks.enums import SessionEndReason
from cc_hooks.models._base import BaseInput, BaseOutput


class SessionEndInput(BaseInput):
    hook_event_name: Literal["SessionEnd"] = Field("SessionEnd", alias="hookEventName")
    reason: str

    def as_known_reason(self) -> SessionEndReason | None:
        try:
            return SessionEndReason(self.reason)
        except ValueError:
            return None


class SessionEndOutput(BaseOutput):
    pass
