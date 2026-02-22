from typing import Literal

from pydantic import Field

from cc_hooks.models._base import BaseInput, BaseOutput


class TeammateIdleInput(BaseInput):
    hook_event_name: Literal["TeammateIdle"] = Field("TeammateIdle", alias="hookEventName")
    teammate_name: str
    team_name: str


class TeammateIdleOutput(BaseOutput):
    pass
