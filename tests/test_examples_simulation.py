import json
import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def _run(script: str, payload: dict) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(EXAMPLES_DIR / script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def test_example_hooks_with_unexpected_payload_fields() -> None:
    cases = [
        (
            "session_start_context.py",
            {
                "session_id": "rt_0",
                "transcript_path": "/tmp/t.jsonl",
                "cwd": "/tmp",
                "permission_mode": "default",
                "hook_event_name": "SessionStart",
                "source": "resume",
                "model": "sonnet",
                "new_start_field": "accepted",
            },
        ),
        (
            "deny_bash_rm.py",
            {
                "session_id": "rt_1",
                "transcript_path": "/tmp/t.jsonl",
                "cwd": "/tmp",
                "permission_mode": "default",
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "rm -rf /tmp/demo"},
                "tool_use_id": "toolu_rt_1",
                "unexpected": "ok",
            },
        ),
        (
            "log_tool_usage.py",
            {
                "session_id": "rt_2",
                "transcript_path": "/tmp/t.jsonl",
                "cwd": "/tmp",
                "permission_mode": "default",
                "hook_event_name": "PostToolUse",
                "tool_name": "Write",
                "tool_input": {"file_path": "/tmp/a.txt", "content": "x"},
                "tool_response": {"ok": True},
                "tool_use_id": "toolu_rt_2",
                "unknown_post": 123,
            },
        ),
        (
            "block_prompt.py",
            {
                "session_id": "rt_3",
                "transcript_path": "/tmp/t.jsonl",
                "cwd": "/tmp",
                "permission_mode": "default",
                "hook_event_name": "UserPromptSubmit",
                "prompt": "a" * 12000,
                "another_new_field": True,
            },
        ),
        (
            "pre_compact_guard.py",
            {
                "session_id": "rt_4",
                "transcript_path": "/tmp/t.jsonl",
                "cwd": "/tmp",
                "permission_mode": "default",
                "hook_event_name": "PreCompact",
                "trigger": "future_trigger",
                "custom_instructions": "summarize",
                "unknown": "still_ok",
            },
        ),
        (
            "stop_block_unless_safe.py",
            {
                "session_id": "rt_5",
                "transcript_path": "/tmp/t.jsonl",
                "cwd": "/tmp",
                "permission_mode": "default",
                "hook_event_name": "Stop",
                "stop_hook_active": True,
                "last_assistant_message": "TODO remains",
                "future_stop_field": "accepted",
            },
        ),
    ]

    for script, payload in cases:
        result = _run(script, payload)
        assert result.returncode == 0, f"{script} failed: {result.stderr}"
