from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class WriteInput(ToolInputBase):
    file_path: str = Field(alias="filePath")
    content: str
