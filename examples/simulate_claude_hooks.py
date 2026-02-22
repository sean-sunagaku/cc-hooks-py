#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CASES = [
    {
        "name": "SessionStart (context added)",
        "script": ROOT / "session_start_context.py",
        "payload": {
            "session_id": "sim_0",
            "transcript_path": "/tmp/t.jsonl",
            "cwd": "/tmp",
            "permission_mode": "default",
            "hook_event_name": "SessionStart",
            "source": "resume",
            "model": "sonnet",
            "unknown_start_field": {"new": "value"}
        },
    },
    {
        "name": "PreToolUse (deny dangerous rm)",
        "script": ROOT / "deny_bash_rm.py",
        "payload": {
            "session_id": "sim_1",
            "transcript_path": "/tmp/t.jsonl",
            "cwd": "/tmp",
            "permission_mode": "default",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /tmp/demo"},
            "tool_use_id": "toolu_1",
            "unexpected_field": "kept_for_forward_compat"
        },
    },
    {
        "name": "PostToolUse (log only, None return)",
        "script": ROOT / "log_tool_usage.py",
        "payload": {
            "session_id": "sim_2",
            "transcript_path": "/tmp/t.jsonl",
            "cwd": "/tmp",
            "permission_mode": "default",
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/a.txt", "content": "x"},
            "tool_response": {"ok": True},
            "tool_use_id": "toolu_2",
            "unknown_post_field": 42
        },
    },
    {
        "name": "UserPromptSubmit (block long prompt)",
        "script": ROOT / "block_prompt.py",
        "payload": {
            "session_id": "sim_3",
            "transcript_path": "/tmp/t.jsonl",
            "cwd": "/tmp",
            "permission_mode": "default",
            "hook_event_name": "UserPromptSubmit",
            "prompt": "a" * 12000,
            "new_field": {"nested": True}
        },
    },
    {
        "name": "PreCompact (unknown trigger accepted)",
        "script": ROOT / "pre_compact_guard.py",
        "payload": {
            "session_id": "sim_4",
            "transcript_path": "/tmp/t.jsonl",
            "cwd": "/tmp",
            "permission_mode": "default",
            "hook_event_name": "PreCompact",
            "trigger": "future_trigger",
            "custom_instructions": "Summarize this session",
            "unknown": "value"
        },
    },
    {
        "name": "Stop (block when TODO remains)",
        "script": ROOT / "stop_block_unless_safe.py",
        "payload": {
            "session_id": "sim_5",
            "transcript_path": "/tmp/t.jsonl",
            "cwd": "/tmp",
            "permission_mode": "default",
            "hook_event_name": "Stop",
            "stop_hook_active": True,
            "last_assistant_message": "There is a TODO left",
            "extra_stop_data": "still accepted"
        },
    },
]


def run_case(name: str, script: Path, payload: dict) -> int:
    result = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )

    print(f"[{name}]")
    print(f"exit={result.returncode}")
    print(f"stdout={result.stdout.strip() or '<empty>'}")
    print(f"stderr={result.stderr.strip() or '<empty>'}")
    print()
    return result.returncode


def main() -> int:
    exit_codes = [run_case(case["name"], case["script"], case["payload"]) for case in CASES]
    return 0 if all(code == 0 for code in exit_codes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
