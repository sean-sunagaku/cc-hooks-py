from typing import Literal

from pydantic import Field

from cc_hooks.enums import ConfigChangeSource
from cc_hooks.models._base import BaseInput, BaseOutput


class ConfigChangeInput(BaseInput):
    hook_event_name: Literal["ConfigChange"] = Field("ConfigChange", alias="hookEventName")
    source: str
    file_path: str | None = Field(None, alias="filePath")

    def as_known_source(self) -> ConfigChangeSource | None:
        try:
            return ConfigChangeSource(self.source)
        except ValueError:
            return None


class ConfigChangeOutput(BaseOutput):
    decision: str | None = None
    reason: str | None = None

    @classmethod
    def ok(cls) -> "ConfigChangeOutput":
        return cls()

    @classmethod
    def block(cls, reason: str) -> "ConfigChangeOutput":
        return cls(decision="block", reason=reason)
