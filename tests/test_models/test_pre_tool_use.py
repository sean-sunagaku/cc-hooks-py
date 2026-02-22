from cc_hooks.enums import PermissionDecision
from cc_hooks.models import PreToolUseInput, PreToolUseOutput


def test_pre_tool_use_input_and_bash_helper(base_payload: dict[str, str]) -> None:
    payload = {
        **base_payload,
        "tool_name": "Bash",
        "tool_input": {"command": "echo hello"},
        "tool_use_id": "toolu_1",
    }
    data = PreToolUseInput(**payload)

    bash = data.as_bash_input()
    assert bash is not None
    assert bash.command == "echo hello"


def test_pre_tool_use_allow_output() -> None:
    output = PreToolUseOutput.allow()
    dumped = output.model_dump(by_alias=True, exclude_none=True)
    assert dumped["hookSpecificOutput"]["permissionDecision"] == PermissionDecision.ALLOW


def test_pre_tool_use_modify_output() -> None:
    output = PreToolUseOutput.modify({"command": "ls"}, reason="normalized")
    dumped = output.model_dump(by_alias=True, exclude_none=True)
    assert dumped["hookSpecificOutput"]["updatedInput"] == {"command": "ls"}
    assert dumped["hookSpecificOutput"]["permissionDecisionReason"] == "normalized"
