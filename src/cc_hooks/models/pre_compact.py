from typing import Literal

from pydantic import Field

from cc_hooks.enums import PreCompactTrigger
from cc_hooks.models._base import BaseInput, BaseOutput


class PreCompactInput(BaseInput):
    hook_event_name: Literal["PreCompact"] = Field("PreCompact", alias="hookEventName")
    trigger: str
    custom_instructions: str = Field(alias="customInstructions")

    def as_known_trigger(self) -> PreCompactTrigger | None:
        try:
            return PreCompactTrigger(self.trigger)
        except ValueError:
            return None


class PreCompactOutput(BaseOutput):
    pass
