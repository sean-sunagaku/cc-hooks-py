from cc_hooks.enums import PreCompactTrigger
from cc_hooks.models import PreCompactInput


def test_pre_compact_accepts_unknown_trigger() -> None:
    model = PreCompactInput(
        session_id="sess_1",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="PreCompact",
        trigger="future_trigger_value",
        custom_instructions="summarize",
    )

    assert model.trigger == "future_trigger_value"
    assert model.as_known_trigger() is None


def test_pre_compact_known_trigger_enum() -> None:
    model = PreCompactInput(
        session_id="sess_2",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="PreCompact",
        trigger="manual",
        custom_instructions="summarize",
    )

    assert model.as_known_trigger() == PreCompactTrigger.MANUAL


def test_pre_compact_known_trigger_auto() -> None:
    model = PreCompactInput(
        session_id="sess_3",
        transcript_path="/tmp/t.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="PreCompact",
        trigger="auto",
        custom_instructions="summarize",
    )

    assert model.as_known_trigger() == PreCompactTrigger.AUTO
