#!/usr/bin/env python3
import io
import json
import sys
from dataclasses import dataclass
from typing import Any, Callable

from cc_hooks.models import (
    ConfigChangeOutput,
    NotificationOutput,
    PermissionRequestOutput,
    PostToolUseFailureOutput,
    PostToolUseOutput,
    PreCompactOutput,
    PreToolUseOutput,
    SessionEndOutput,
    SessionStartOutput,
    StopOutput,
    SubagentStartOutput,
    SubagentStopOutput,
    TaskCompletedOutput,
    TeammateIdleOutput,
    UserPromptSubmitOutput,
)
from cc_hooks.runner import _execute


@dataclass
class Case:
    event: str
    payload: dict[str, Any]
    handler: Callable[[Any], Any]


def _base(event: str) -> dict[str, Any]:
    return {
        "session_id": f"e2e_{event}",
        "transcript_path": "/tmp/e2e.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": event,
    }


def _run(case: Case) -> tuple[int, str, str]:
    old_stdin, old_stdout, old_stderr = sys.stdin, sys.stdout, sys.stderr
    stdin = io.StringIO(json.dumps(case.payload))
    stdout = io.StringIO()
    stderr = io.StringIO()
    sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr
    try:
        _execute(case.handler, case.event)
    except SystemExit as exc:
        return int(exc.code), stdout.getvalue(), stderr.getvalue()
    finally:
        sys.stdin, sys.stdout, sys.stderr = old_stdin, old_stdout, old_stderr
    return 1, stdout.getvalue(), stderr.getvalue()


CASES: list[Case] = [
    Case(
        "SessionStart",
        {**_base("SessionStart"), "source": "startup", "model": "sonnet", "future": 1},
        lambda _: SessionStartOutput.add_context("ok"),
    ),
    Case("SessionEnd", {**_base("SessionEnd"), "reason": "clear"}, lambda _: SessionEndOutput()),
    Case(
        "UserPromptSubmit",
        {**_base("UserPromptSubmit"), "prompt": "hello"},
        lambda _: UserPromptSubmitOutput.ok(),
    ),
    Case(
        "PreToolUse",
        {
            **_base("PreToolUse"),
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/a.txt"},
            "tool_use_id": "toolu_pre",
        },
        lambda _: PreToolUseOutput.allow(),
    ),
    Case(
        "PostToolUse",
        {
            **_base("PostToolUse"),
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/a.txt"},
            "tool_response": {"content": "x"},
            "tool_use_id": "toolu_post",
        },
        lambda _: PostToolUseOutput.ok(),
    ),
    Case(
        "PostToolUseFailure",
        {
            **_base("PostToolUseFailure"),
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/a.txt"},
            "tool_use_id": "toolu_fail",
            "error": "boom",
        },
        lambda _: PostToolUseFailureOutput.add_context("noted"),
    ),
    Case(
        "PermissionRequest",
        {
            **_base("PermissionRequest"),
            "tool_name": "Bash",
            "tool_input": {"command": "echo ok"},
        },
        lambda _: PermissionRequestOutput.allow("approved"),
    ),
    Case(
        "Notification",
        {**_base("Notification"), "message": "hello", "notification_type": "info"},
        lambda _: NotificationOutput(),
    ),
    Case(
        "SubagentStart",
        {**_base("SubagentStart"), "agent_id": "a1", "agent_type": "researcher"},
        lambda _: SubagentStartOutput(),
    ),
    Case(
        "SubagentStop",
        {
            **_base("SubagentStop"),
            "stop_hook_active": True,
            "agent_id": "a1",
            "agent_type": "researcher",
            "agent_transcript_path": "/tmp/a1.jsonl",
        },
        lambda _: SubagentStopOutput.ok(),
    ),
    Case(
        "Stop",
        {**_base("Stop"), "stop_hook_active": True},
        lambda _: StopOutput.ok(),
    ),
    Case(
        "TeammateIdle",
        {**_base("TeammateIdle"), "teammate_name": "alice", "team_name": "red"},
        lambda _: TeammateIdleOutput(),
    ),
    Case(
        "TaskCompleted",
        {**_base("TaskCompleted"), "task_id": "t1", "task_subject": "task"},
        lambda _: TaskCompletedOutput(),
    ),
    Case(
        "ConfigChange",
        {**_base("ConfigChange"), "source": "user"},
        lambda _: ConfigChangeOutput.ok(),
    ),
    Case(
        "PreCompact",
        {**_base("PreCompact"), "trigger": "auto", "custom_instructions": "summarize"},
        lambda _: PreCompactOutput(),
    ),
]


def main() -> int:
    failed: list[str] = []
    for case in CASES:
        code, out, err = _run(case)
        if code != 0:
            failed.append(f"{case.event}: exit={code} stderr={err!r}")
            continue
        if err.strip():
            failed.append(f"{case.event}: unexpected stderr={err!r}")
            continue
        if out.strip():
            try:
                json.loads(out)
            except json.JSONDecodeError:
                failed.append(f"{case.event}: stdout is not JSON: {out!r}")

    if failed:
        print("[e2e-all-hooks] failed")
        for item in failed:
            print("-", item)
        return 1

    print(f"[e2e-all-hooks] success: {len(CASES)} events validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
