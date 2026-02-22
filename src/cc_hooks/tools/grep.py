from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class GrepInput(ToolInputBase):
    pattern: str
    path: str | None = None
    include: str | None = None
    multiline: bool | None = None
    ignore_case: bool | None = Field(None, alias="ignoreCase")
