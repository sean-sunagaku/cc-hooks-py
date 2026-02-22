from cc_hooks.enums import SessionEndReason, SessionStartSource
from cc_hooks.models import SessionEndInput, SessionStartInput


def test_session_start_known_source() -> None:
    model = SessionStartInput(
        session_id="sess_start_1",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="SessionStart",
        source="resume",
        model="sonnet",
    )
    assert model.as_known_source() == SessionStartSource.RESUME


def test_session_start_unknown_source() -> None:
    model = SessionStartInput(
        session_id="sess_start_2",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="SessionStart",
        source="future_source",
        model="sonnet",
    )
    assert model.as_known_source() is None


def test_session_end_known_reason() -> None:
    model = SessionEndInput(
        session_id="sess_end_1",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="SessionEnd",
        reason="clear",
    )
    assert model.as_known_reason() == SessionEndReason.CLEAR


def test_session_end_unknown_reason() -> None:
    model = SessionEndInput(
        session_id="sess_end_2",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="SessionEnd",
        reason="future_reason",
    )
    assert model.as_known_reason() is None
