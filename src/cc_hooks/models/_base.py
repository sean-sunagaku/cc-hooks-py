from pydantic import BaseModel, ConfigDict, Field

from cc_hooks.enums import PermissionMode


class BaseInput(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    session_id: str = Field(alias="sessionId")
    transcript_path: str = Field(alias="transcriptPath")
    cwd: str
    permission_mode: str = Field(alias="permissionMode")
    hook_event_name: str = Field(alias="hookEventName")

    def as_known_permission_mode(self) -> PermissionMode | None:
        try:
            return PermissionMode(self.permission_mode)
        except ValueError:
            return None


class BaseOutput(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True, serialize_by_alias=True)

    continue_: bool | None = Field(None, alias="continue")
    stop_reason: str | None = Field(None, alias="stopReason")
    suppress_output: bool | None = Field(None, alias="suppressOutput")
    system_message: str | None = Field(None, alias="systemMessage")

    @classmethod
    def stop_session(cls, reason: str) -> "BaseOutput":
        return cls(continue_=False, stop_reason=reason)
