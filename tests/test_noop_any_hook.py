import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "examples" / "noop_any_hook.py"


def _run(payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def test_noop_any_hook_accepts_remaining_supported_events() -> None:
    base = {
        "session_id": "noop_0",
        "transcript_path": "/tmp/noop.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
    }
    cases = [
        {**base, "hook_event_name": "SessionEnd", "reason": "other"},
        {
            **base,
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/a.txt"},
            "tool_use_id": "toolu_fail",
            "error": "boom",
        },
        {
            **base,
            "hook_event_name": "PermissionRequest",
            "tool_name": "Bash",
            "tool_input": {"command": "echo ok"},
        },
        {
            **base,
            "hook_event_name": "Notification",
            "message": "hello",
            "notification_type": "info",
        },
        {
            **base,
            "hook_event_name": "SubagentStart",
            "agent_id": "a1",
            "agent_type": "researcher",
        },
        {
            **base,
            "hook_event_name": "SubagentStop",
            "stop_hook_active": True,
            "agent_id": "a1",
            "agent_type": "researcher",
            "agent_transcript_path": "/tmp/a1.jsonl",
        },
        {
            **base,
            "hook_event_name": "TeammateIdle",
            "teammate_name": "alice",
            "team_name": "red",
        },
        {
            **base,
            "hook_event_name": "TaskCompleted",
            "task_id": "t1",
            "task_subject": "task",
        },
        {
            **base,
            "hook_event_name": "ConfigChange",
            "source": "user",
        },
    ]

    for payload in cases:
        result = _run(payload)
        assert result.returncode == 0, result.stderr
        assert result.stdout == ""
