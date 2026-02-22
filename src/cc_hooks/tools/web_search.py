from pydantic import Field

from cc_hooks.tools._base import ToolInputBase


class WebSearchInput(ToolInputBase):
    query: str
    recency_days: int | None = Field(None, alias="recencyDays")
