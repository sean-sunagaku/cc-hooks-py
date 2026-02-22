from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class NotebookEditInput(ToolInputBase):
    notebook_path: str = Field(alias="notebookPath")
    cell_id: str | None = Field(None, alias="cellId")
    edit: str | None = None
    content: str | None = None
