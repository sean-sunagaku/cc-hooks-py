from typing import Literal

from pydantic import Field

from cc_hooks.models._base import BaseInput, BaseOutput


class SubagentStopInput(BaseInput):
    hook_event_name: Literal["SubagentStop"] = Field("SubagentStop", alias="hookEventName")
    stop_hook_active: bool = Field(alias="stopHookActive")
    agent_id: str = Field(alias="agentId")
    agent_type: str = Field(alias="agentType")
    agent_transcript_path: str = Field(alias="agentTranscriptPath")
    last_assistant_message: str | None = Field(None, alias="lastAssistantMessage")


class SubagentStopOutput(BaseOutput):
    decision: str | None = None
    reason: str | None = None

    @classmethod
    def ok(cls) -> "SubagentStopOutput":
        return cls()

    @classmethod
    def block(cls, reason: str) -> "SubagentStopOutput":
        return cls(decision="block", reason=reason)
