from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class GlobInput(ToolInputBase):
    pattern: str
    path: str | None = None
    case_sensitive: bool | None = Field(None, alias="caseSensitive")
