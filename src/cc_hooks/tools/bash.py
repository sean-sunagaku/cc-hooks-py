from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class BashInput(ToolInputBase):
    command: str
    description: str | None = None
    timeout: int | None = None
    run_in_background: bool | None = Field(None, alias="runInBackground")
