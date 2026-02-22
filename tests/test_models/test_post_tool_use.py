from cc_hooks.models import PostToolUseInput, PostToolUseOutput


def test_post_tool_use_input_and_helpers(base_payload: dict[str, str]) -> None:
    payload = {
        **base_payload,
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/a.txt", "content": "x"},
        "tool_response": {"ok": True},
        "tool_use_id": "toolu_2",
    }
    data = PostToolUseInput(**payload)

    write_input = data.as_write_input()
    assert write_input is not None
    assert write_input.file_path == "/tmp/a.txt"


def test_post_tool_use_block_output() -> None:
    output = PostToolUseOutput.block("failed policy")
    dumped = output.model_dump(by_alias=True, exclude_none=True)
    assert dumped["decision"] == "block"
    assert dumped["reason"] == "failed policy"
