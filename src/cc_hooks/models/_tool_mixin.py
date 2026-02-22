from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from cc_hooks.enums import BuiltinToolName
from cc_hooks.registry import get_tool_input_model
from cc_hooks.tools import (
    BashInput,
    EditInput,
    GlobInput,
    GrepInput,
    NotebookEditInput,
    ReadInput,
    TaskInput,
    WebFetchInput,
    WebSearchInput,
    WriteInput,
)

T = TypeVar("T", bound=BaseModel)


class ToolInputParsingMixin:
    tool_name: str
    tool_input: dict[str, Any]

    def as_tool_input(self, model: type[T]) -> T | None:
        try:
            return model(**self.tool_input)
        except ValidationError:
            return None

    def as_builtin_tool_name(self) -> BuiltinToolName | None:
        try:
            return BuiltinToolName(self.tool_name)
        except ValueError:
            return None

    def as_registered_tool_input(self) -> BaseModel | None:
        model = get_tool_input_model(self.tool_name)
        if model is None:
            return None
        return self.as_tool_input(model)

    def as_bash_input(self) -> BashInput | None:
        return self.as_tool_input(BashInput) if self.tool_name == "Bash" else None

    def as_write_input(self) -> WriteInput | None:
        return self.as_tool_input(WriteInput) if self.tool_name == "Write" else None

    def as_edit_input(self) -> EditInput | None:
        return self.as_tool_input(EditInput) if self.tool_name == "Edit" else None

    def as_read_input(self) -> ReadInput | None:
        return self.as_tool_input(ReadInput) if self.tool_name == "Read" else None

    def as_glob_input(self) -> GlobInput | None:
        return self.as_tool_input(GlobInput) if self.tool_name == "Glob" else None

    def as_grep_input(self) -> GrepInput | None:
        return self.as_tool_input(GrepInput) if self.tool_name == "Grep" else None

    def as_web_fetch_input(self) -> WebFetchInput | None:
        return self.as_tool_input(WebFetchInput) if self.tool_name == "WebFetch" else None

    def as_web_search_input(self) -> WebSearchInput | None:
        return self.as_tool_input(WebSearchInput) if self.tool_name == "WebSearch" else None

    def as_task_input(self) -> TaskInput | None:
        return self.as_tool_input(TaskInput) if self.tool_name == "Task" else None

    def as_notebook_edit_input(self) -> NotebookEditInput | None:
        return self.as_tool_input(NotebookEditInput) if self.tool_name == "NotebookEdit" else None
