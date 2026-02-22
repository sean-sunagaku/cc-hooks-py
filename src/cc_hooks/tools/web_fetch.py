from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class WebFetchInput(ToolInputBase):
    url: str
    prompt: str | None = None
    timeout_ms: int | None = Field(None, alias="timeoutMs")
