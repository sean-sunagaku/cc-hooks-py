from cc_hooks.enums import (
    BuiltinToolName,
    ConfigChangeSource,
    NotificationType,
    PermissionMode,
)
from cc_hooks.models import ConfigChangeInput, NotificationInput, PreToolUseInput


def test_base_input_known_permission_mode() -> None:
    model = NotificationInput(
        session_id="sess_n1",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="Notification",
        message="hello",
        notification_type="info",
    )
    assert model.as_known_permission_mode() == PermissionMode.DEFAULT


def test_base_input_unknown_permission_mode() -> None:
    model = NotificationInput(
        session_id="sess_n2",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="future_mode",
        hook_event_name="Notification",
        message="hello",
        notification_type="info",
    )
    assert model.as_known_permission_mode() is None


def test_tool_input_known_builtin_tool_name() -> None:
    model = PreToolUseInput(
        session_id="sess_t1",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="PreToolUse",
        tool_name="Bash",
        tool_input={"command": "echo hello"},
        tool_use_id="toolu_x",
    )
    assert model.as_builtin_tool_name() == BuiltinToolName.BASH


def test_tool_input_unknown_builtin_tool_name() -> None:
    model = PreToolUseInput(
        session_id="sess_t2",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="PreToolUse",
        tool_name="mcp__custom__tool",
        tool_input={"x": 1},
        tool_use_id="toolu_y",
    )
    assert model.as_builtin_tool_name() is None


def test_notification_known_type() -> None:
    model = NotificationInput(
        session_id="sess_n3",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="Notification",
        message="hello",
        notification_type="warning",
    )
    assert model.as_known_notification_type() == NotificationType.WARNING


def test_notification_unknown_type() -> None:
    model = NotificationInput(
        session_id="sess_n4",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="Notification",
        message="hello",
        notification_type="future_notification",
    )
    assert model.as_known_notification_type() is None


def test_config_change_known_source() -> None:
    model = ConfigChangeInput(
        session_id="sess_c1",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="ConfigChange",
        source="user",
    )
    assert model.as_known_source() == ConfigChangeSource.USER


def test_config_change_unknown_source() -> None:
    model = ConfigChangeInput(
        session_id="sess_c2",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="ConfigChange",
        source="future_source",
    )
    assert model.as_known_source() is None
