from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from cc_hooks.enums import PermissionDecision
from cc_hooks.models._base import BaseInput, BaseOutput
from cc_hooks.models._tool_mixin import ToolInputParsingMixin


class PreToolUseInput(BaseInput, ToolInputParsingMixin):
    hook_event_name: Literal["PreToolUse"] = Field("PreToolUse", alias="hookEventName")
    tool_name: str = Field(alias="toolName")
    tool_input: dict[str, Any] = Field(alias="toolInput")
    tool_use_id: str = Field(alias="toolUseId")


class PreToolUseHookSpecific(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    hook_event_name: Literal["PreToolUse"] = Field("PreToolUse", alias="hookEventName")
    permission_decision: PermissionDecision | None = Field(None, alias="permissionDecision")
    permission_decision_reason: str | None = Field(None, alias="permissionDecisionReason")
    updated_input: dict[str, Any] | None = Field(None, alias="updatedInput")
    additional_context: str | None = Field(None, alias="additionalContext")


class PreToolUseOutput(BaseOutput):
    hook_specific_output: PreToolUseHookSpecific | None = Field(None, alias="hookSpecificOutput")

    @classmethod
    def allow(cls) -> "PreToolUseOutput":
        return cls(
            hook_specific_output=PreToolUseHookSpecific(permission_decision=PermissionDecision.ALLOW),
        )

    @classmethod
    def deny(cls, reason: str) -> "PreToolUseOutput":
        return cls(
            hook_specific_output=PreToolUseHookSpecific(
                permission_decision=PermissionDecision.DENY,
                permission_decision_reason=reason,
            ),
        )

    @classmethod
    def ask(cls, reason: str) -> "PreToolUseOutput":
        return cls(
            hook_specific_output=PreToolUseHookSpecific(
                permission_decision=PermissionDecision.ASK,
                permission_decision_reason=reason,
            ),
        )

    @classmethod
    def modify(cls, updated_input: dict[str, Any], reason: str | None = None) -> "PreToolUseOutput":
        return cls(
            hook_specific_output=PreToolUseHookSpecific(
                permission_decision=PermissionDecision.ALLOW,
                updated_input=updated_input,
                permission_decision_reason=reason,
            ),
        )

    @classmethod
    def add_context(cls, context: str) -> "PreToolUseOutput":
        return cls(hook_specific_output=PreToolUseHookSpecific(additional_context=context))
