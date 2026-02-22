from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from cc_hooks.models._base import BaseInput, BaseOutput
from cc_hooks.models._tool_mixin import ToolInputParsingMixin


class PostToolUseInput(BaseInput, ToolInputParsingMixin):
    hook_event_name: Literal["PostToolUse"] = Field("PostToolUse", alias="hookEventName")
    tool_name: str = Field(alias="toolName")
    tool_input: dict[str, Any] = Field(alias="toolInput")
    tool_response: dict[str, Any] = Field(alias="toolResponse")
    tool_use_id: str = Field(alias="toolUseId")


class PostToolUseHookSpecific(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    hook_event_name: Literal["PostToolUse"] = Field("PostToolUse", alias="hookEventName")
    additional_context: str | None = Field(None, alias="additionalContext")
    updated_mcp_tool_output: dict[str, Any] | None = Field(None, alias="updatedMCPToolOutput")


class PostToolUseOutput(BaseOutput):
    decision: str | None = None
    reason: str | None = None
    hook_specific_output: PostToolUseHookSpecific | None = Field(None, alias="hookSpecificOutput")

    @classmethod
    def ok(cls) -> "PostToolUseOutput":
        return cls()

    @classmethod
    def block(cls, reason: str) -> "PostToolUseOutput":
        return cls(decision="block", reason=reason)

    @classmethod
    def add_context(cls, context: str) -> "PostToolUseOutput":
        return cls(hook_specific_output=PostToolUseHookSpecific(additional_context=context))

    @classmethod
    def update_tool_output(cls, updated_output: dict[str, Any]) -> "PostToolUseOutput":
        return cls(hook_specific_output=PostToolUseHookSpecific(updated_mcp_tool_output=updated_output))
