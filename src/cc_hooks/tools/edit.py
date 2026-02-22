from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class EditInput(ToolInputBase):
    file_path: str = Field(alias="filePath")
    old_string: str = Field(alias="oldString")
    new_string: str = Field(alias="newString")
    replace_all: bool = Field(False, alias="replaceAll")
