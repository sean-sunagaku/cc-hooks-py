from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from cc_hooks.models._base import BaseInput, BaseOutput
from cc_hooks.models._tool_mixin import ToolInputParsingMixin


class PermissionRequestInput(BaseInput, ToolInputParsingMixin):
    hook_event_name: Literal["PermissionRequest"] = Field("PermissionRequest", alias="hookEventName")
    tool_name: str = Field(alias="toolName")
    tool_input: dict[str, Any] = Field(alias="toolInput")
    permission_suggestions: list[dict[str, Any]] | None = Field(None, alias="permissionSuggestions")


class PermissionRequestDecision(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    behavior: Literal["allow", "deny", "ask"]
    message: str | None = None
    updated_input: dict[str, Any] | None = Field(None, alias="updatedInput")


class PermissionRequestHookSpecific(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    hook_event_name: Literal["PermissionRequest"] = Field("PermissionRequest", alias="hookEventName")
    decision: PermissionRequestDecision | None = None


class PermissionRequestOutput(BaseOutput):
    hook_specific_output: PermissionRequestHookSpecific | None = Field(None, alias="hookSpecificOutput")

    @classmethod
    def allow(cls, message: str | None = None) -> "PermissionRequestOutput":
        return cls(
            hook_specific_output=PermissionRequestHookSpecific(
                decision=PermissionRequestDecision(behavior="allow", message=message),
            ),
        )

    @classmethod
    def deny(cls, message: str | None = None) -> "PermissionRequestOutput":
        return cls(
            hook_specific_output=PermissionRequestHookSpecific(
                decision=PermissionRequestDecision(behavior="deny", message=message),
            ),
        )

    @classmethod
    def ask(cls, message: str | None = None) -> "PermissionRequestOutput":
        return cls(
            hook_specific_output=PermissionRequestHookSpecific(
                decision=PermissionRequestDecision(behavior="ask", message=message),
            ),
        )

    @classmethod
    def modify_and_allow(cls, updated_input: dict[str, Any], message: str | None = None) -> "PermissionRequestOutput":
        return cls(
            hook_specific_output=PermissionRequestHookSpecific(
                decision=PermissionRequestDecision(behavior="allow", message=message, updated_input=updated_input),
            ),
        )
