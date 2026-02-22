from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class TaskInput(ToolInputBase):
    description: str
    prompt: str
    subagent_type: str | None = Field(None, alias="subagentType")
