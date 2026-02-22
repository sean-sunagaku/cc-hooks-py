import pytest


@pytest.fixture
def base_payload() -> dict[str, str]:
    return {
        "session_id": "sess_123",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/tmp",
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
    }
