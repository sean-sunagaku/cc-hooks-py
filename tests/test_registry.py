from pydantic import BaseModel

from cc_hooks.registry import get_tool_input_model, register_tool_input


class CustomInput(BaseModel):
    value: str


def test_registry_has_builtins() -> None:
    assert get_tool_input_model("Bash") is not None
    assert get_tool_input_model("Write") is not None


def test_register_custom_tool() -> None:
    register_tool_input("mcp__custom__tool", CustomInput)
    model = get_tool_input_model("mcp__custom__tool")
    assert model is CustomInput
