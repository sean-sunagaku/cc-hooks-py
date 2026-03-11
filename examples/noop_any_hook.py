#!/usr/bin/env python3
import json
import sys

from cc_hooks.models import (
    ConfigChangeInput,
    NotificationInput,
    PermissionRequestInput,
    PostToolUseFailureInput,
    PostToolUseInput,
    PreCompactInput,
    PreToolUseInput,
    SessionEndInput,
    SessionStartInput,
    StopInput,
    SubagentStartInput,
    SubagentStopInput,
    TaskCompletedInput,
    TeammateIdleInput,
    UserPromptSubmitInput,
)

INPUT_MODELS = {
    "SessionStart": SessionStartInput,
    "SessionEnd": SessionEndInput,
    "UserPromptSubmit": UserPromptSubmitInput,
    "PreToolUse": PreToolUseInput,
    "PostToolUse": PostToolUseInput,
    "PostToolUseFailure": PostToolUseFailureInput,
    "PermissionRequest": PermissionRequestInput,
    "Notification": NotificationInput,
    "SubagentStart": SubagentStartInput,
    "SubagentStop": SubagentStopInput,
    "Stop": StopInput,
    "TeammateIdle": TeammateIdleInput,
    "TaskCompleted": TaskCompletedInput,
    "ConfigChange": ConfigChangeInput,
    "PreCompact": PreCompactInput,
}


def main() -> int:
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw else {}
    event = payload.get("hook_event_name") or payload.get("hookEventName")
    if not isinstance(event, str) or event not in INPUT_MODELS:
        raise SystemExit(f"Unsupported hook event: {event!r}")

    INPUT_MODELS[event](**payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
