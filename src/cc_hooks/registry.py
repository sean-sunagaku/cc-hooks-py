from pydantic import BaseModel

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

_tool_registry: dict[str, type[BaseModel]] = {}


def register_tool_input(tool_name: str, model: type[BaseModel]) -> None:
    _tool_registry[tool_name] = model


def get_tool_input_model(tool_name: str) -> type[BaseModel] | None:
    return _tool_registry.get(tool_name)


def _register_builtins() -> None:
    register_tool_input("Bash", BashInput)
    register_tool_input("Write", WriteInput)
    register_tool_input("Edit", EditInput)
    register_tool_input("Read", ReadInput)
    register_tool_input("Glob", GlobInput)
    register_tool_input("Grep", GrepInput)
    register_tool_input("WebFetch", WebFetchInput)
    register_tool_input("WebSearch", WebSearchInput)
    register_tool_input("Task", TaskInput)
    register_tool_input("NotebookEdit", NotebookEditInput)


_register_builtins()

__all__ = ["register_tool_input", "get_tool_input_model"]
