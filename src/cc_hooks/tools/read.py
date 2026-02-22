from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class ReadInput(ToolInputBase):
    file_path: str = Field(alias="filePath")
    offset: int | None = None
    limit: int | None = None
