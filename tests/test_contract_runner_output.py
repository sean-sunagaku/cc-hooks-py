import io
import json
from pathlib import Path
from typing import Any, Callable

import pytest

from cc_hooks.models import (
    PermissionRequestOutput,
    PostToolUseOutput,
    PreToolUseOutput,
    SessionStartOutput,
    StopOutput,
    UserPromptSubmitOutput,
)
from cc_hooks.runner import _execute

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def _run_execute(
    monkeypatch: pytest.MonkeyPatch,
    event: str,
    payload: dict[str, Any],
    handler: Callable[[Any], Any],
) -> dict[str, Any]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setattr("sys.stdout", stdout)
    monkeypatch.setattr("sys.stderr", stderr)

    with pytest.raises(SystemExit) as exc:
        _execute(handler, event)

    assert exc.value.code == 0
    assert stderr.getvalue() == ""
    return json.loads(stdout.getvalue())


def _load_snapshot(name: str) -> dict[str, Any]:
    return json.loads((SNAPSHOT_DIR / name).read_text(encoding="utf-8"))


def test_contract_session_start_output_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s_contract_1",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "SessionStart",
        "source": "cli",
        "model": "sonnet",
    }

    def handler(_: Any) -> SessionStartOutput:
        return SessionStartOutput.add_context("session started")

    actual = _run_execute(monkeypatch, "SessionStart", payload, handler)
    expected = _load_snapshot("session_start_add_context.json")
    assert actual == expected


def test_contract_pre_tool_use_output_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s_contract_2",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "echo hello"},
        "tool_use_id": "toolu_contract_2",
    }

    def handler(_: Any) -> PreToolUseOutput:
        return PreToolUseOutput.allow()

    actual = _run_execute(monkeypatch, "PreToolUse", payload, handler)
    expected = _load_snapshot("pre_tool_use_allow.json")
    assert actual == expected


def test_contract_stop_output_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s_contract_3",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "Stop",
        "stop_hook_active": True,
        "last_assistant_message": "done",
    }

    def handler(_: Any) -> StopOutput:
        return StopOutput.block("Need test coverage")

    actual = _run_execute(monkeypatch, "Stop", payload, handler)
    expected = _load_snapshot("stop_block.json")
    assert actual == expected


def test_contract_permission_request_allow_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s_contract_4",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "PermissionRequest",
        "tool_name": "Bash",
        "tool_input": {"command": "echo ok"},
        "permission_suggestions": [{"behavior": "allow"}],
    }

    def handler(_: Any) -> PermissionRequestOutput:
        return PermissionRequestOutput.allow("approved")

    actual = _run_execute(monkeypatch, "PermissionRequest", payload, handler)
    expected = _load_snapshot("permission_request_allow.json")
    assert actual == expected


def test_contract_post_tool_use_update_output_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s_contract_5",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {"file_path": "/tmp/a.txt"},
        "tool_response": {"content": "x"},
        "tool_use_id": "toolu_contract_5",
    }

    def handler(_: Any) -> PostToolUseOutput:
        return PostToolUseOutput.update_tool_output({"summary": "normalized"})

    actual = _run_execute(monkeypatch, "PostToolUse", payload, handler)
    expected = _load_snapshot("post_tool_use_update_tool_output.json")
    assert actual == expected


def test_contract_user_prompt_submit_block_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s_contract_6",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "a" * 12000,
    }

    def handler(_: Any) -> UserPromptSubmitOutput:
        return UserPromptSubmitOutput.block("Prompt too long")

    actual = _run_execute(monkeypatch, "UserPromptSubmit", payload, handler)
    expected = _load_snapshot("user_prompt_submit_block.json")
    assert actual == expected
