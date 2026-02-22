from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from cc_hooks.enums import SessionStartSource
from cc_hooks.models._base import BaseInput, BaseOutput


class SessionStartInput(BaseInput):
    hook_event_name: Literal["SessionStart"] = Field("SessionStart", alias="hookEventName")
    source: str
    model: str
    agent_type: str | None = Field(None, alias="agentType")

    def as_known_source(self) -> SessionStartSource | None:
        try:
            return SessionStartSource(self.source)
        except ValueError:
            return None


class SessionStartHookSpecific(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    hook_event_name: Literal["SessionStart"] = Field("SessionStart", alias="hookEventName")
    additional_context: str | None = Field(None, alias="additionalContext")


class SessionStartOutput(BaseOutput):
    hook_specific_output: SessionStartHookSpecific | None = Field(None, alias="hookSpecificOutput")

    @classmethod
    def add_context(cls, context: str) -> "SessionStartOutput":
        return cls(hook_specific_output=SessionStartHookSpecific(additional_context=context))
