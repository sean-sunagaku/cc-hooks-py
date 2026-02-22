import io
import json
from typing import Any

import pytest

from cc_hooks.models import NotificationOutput, SessionEndOutput, SessionStartOutput
from cc_hooks.runner import _execute


def _set_stdio(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> tuple[io.StringIO, io.StringIO]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setattr("sys.stdout", stdout)
    monkeypatch.setattr("sys.stderr", stderr)
    return stdout, stderr


def test_execute_sync_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s1",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "SessionStart",
        "source": "cli",
        "model": "sonnet",
    }

    def handler(_: Any) -> SessionStartOutput:
        return SessionStartOutput.add_context("ok")

    stdout, _ = _set_stdio(monkeypatch, payload)
    with pytest.raises(SystemExit) as exc:
        _execute(handler, "SessionStart")

    assert exc.value.code == 0
    output = json.loads(stdout.getvalue())
    assert output["hookSpecificOutput"]["additionalContext"] == "ok"


def test_execute_async_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s2",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "SessionEnd",
        "reason": "user",
    }

    async def handler(_: Any) -> SessionEndOutput:
        return SessionEndOutput()

    stdout, _ = _set_stdio(monkeypatch, payload)
    with pytest.raises(SystemExit) as exc:
        _execute(handler, "SessionEnd")

    assert exc.value.code == 0
    assert stdout.getvalue() == "{}"


def test_execute_none_return(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s3",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "Notification",
        "message": "m",
        "notification_type": "info",
    }

    def handler(_: Any) -> None:
        return None

    stdout, _ = _set_stdio(monkeypatch, payload)
    with pytest.raises(SystemExit) as exc:
        _execute(handler, "Notification")

    assert exc.value.code == 0
    assert stdout.getvalue() == ""


def test_execute_error_returns_exit_2(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "session_id": "s4",
        "transcript_path": "/tmp/t.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "Notification",
        "message": "m",
        "notification_type": "info",
    }

    def handler(_: Any) -> NotificationOutput:
        raise RuntimeError("boom")

    _, stderr = _set_stdio(monkeypatch, payload)
    with pytest.raises(SystemExit) as exc:
        _execute(handler, "Notification")

    assert exc.value.code == 2
    assert "RuntimeError" in stderr.getvalue()
    assert "event=Notification" in stderr.getvalue()
    assert "handler=handler" in stderr.getvalue()
