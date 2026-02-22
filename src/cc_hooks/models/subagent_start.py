from typing import Literal

from pydantic import Field

from cc_hooks.models._base import BaseInput, BaseOutput


class SubagentStartInput(BaseInput):
    hook_event_name: Literal["SubagentStart"] = Field("SubagentStart", alias="hookEventName")
    agent_id: str = Field(alias="agentId")
    agent_type: str = Field(alias="agentType")


class SubagentStartOutput(BaseOutput):
    pass
