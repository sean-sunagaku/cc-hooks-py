from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from cc_hooks.models._base import BaseInput, BaseOutput


class UserPromptSubmitInput(BaseInput):
    hook_event_name: Literal["UserPromptSubmit"] = Field("UserPromptSubmit", alias="hookEventName")
    prompt: str


class UserPromptSubmitHookSpecific(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    hook_event_name: Literal["UserPromptSubmit"] = Field("UserPromptSubmit", alias="hookEventName")
    additional_context: str | None = Field(None, alias="additionalContext")


class UserPromptSubmitOutput(BaseOutput):
    decision: str | None = None
    reason: str | None = None
    hook_specific_output: UserPromptSubmitHookSpecific | None = Field(None, alias="hookSpecificOutput")

    @classmethod
    def ok(cls) -> "UserPromptSubmitOutput":
        return cls()

    @classmethod
    def block(cls, reason: str) -> "UserPromptSubmitOutput":
        return cls(decision="block", reason=reason)

    @classmethod
    def add_context(cls, context: str) -> "UserPromptSubmitOutput":
        return cls(hook_specific_output=UserPromptSubmitHookSpecific(additional_context=context))
