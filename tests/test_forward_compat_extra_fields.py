from cc_hooks.models import NotificationInput, SessionStartInput


def test_unknown_fields_are_accepted_notification() -> None:
    model = NotificationInput(
        session_id="s1",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="Notification",
        message="hello",
        notification_type="info",
        brand_new_field="future",
    )
    assert getattr(model, "brand_new_field") == "future"


def test_unknown_fields_are_accepted_session_start() -> None:
    model = SessionStartInput(
        session_id="s2",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="SessionStart",
        source="startup",
        model="sonnet",
        new_nested={"ok": True},
    )
    assert getattr(model, "new_nested") == {"ok": True}
