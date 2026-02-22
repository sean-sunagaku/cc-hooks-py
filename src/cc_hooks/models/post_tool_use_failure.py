from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from cc_hooks.models._base import BaseInput, BaseOutput
from cc_hooks.models._tool_mixin import ToolInputParsingMixin


class PostToolUseFailureInput(BaseInput, ToolInputParsingMixin):
    hook_event_name: Literal["PostToolUseFailure"] = Field("PostToolUseFailure", alias="hookEventName")
    tool_name: str = Field(alias="toolName")
    tool_input: dict[str, Any] = Field(alias="toolInput")
    tool_use_id: str = Field(alias="toolUseId")
    error: str
    is_interrupt: bool | None = Field(None, alias="isInterrupt")


class PostToolUseFailureHookSpecific(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    hook_event_name: Literal["PostToolUseFailure"] = Field("PostToolUseFailure", alias="hookEventName")
    additional_context: str | None = Field(None, alias="additionalContext")


class PostToolUseFailureOutput(BaseOutput):
    hook_specific_output: PostToolUseFailureHookSpecific | None = Field(None, alias="hookSpecificOutput")

    @classmethod
    def add_context(cls, context: str) -> "PostToolUseFailureOutput":
        return cls(hook_specific_output=PostToolUseFailureHookSpecific(additional_context=context))
