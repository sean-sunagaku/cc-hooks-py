from typing import Literal

from pydantic import Field

from cc_hooks.models._base import BaseInput, BaseOutput


class StopInput(BaseInput):
    hook_event_name: Literal["Stop"] = Field("Stop", alias="hookEventName")
    stop_hook_active: bool = Field(alias="stopHookActive")
    last_assistant_message: str | None = Field(None, alias="lastAssistantMessage")


class StopOutput(BaseOutput):
    decision: str | None = None
    reason: str | None = None

    @classmethod
    def ok(cls) -> "StopOutput":
        return cls()

    @classmethod
    def block(cls, reason: str) -> "StopOutput":
        return cls(decision="block", reason=reason)
