import json
from pathlib import Path

from cc_hooks.enums import HookEvent


ROOT = Path(__file__).resolve().parent.parent
SETTINGS = ROOT / "examples" / "claude_hooks_settings.json"


def test_example_settings_register_all_supported_hook_events() -> None:
    config = json.loads(SETTINGS.read_text(encoding="utf-8"))

    expected_events = {event.value for event in HookEvent}
    assert set(config["hooks"]) == expected_events

    for event, matcher_groups in config["hooks"].items():
        assert isinstance(matcher_groups, list), event
        assert matcher_groups, event

        for group in matcher_groups:
            assert isinstance(group, dict), event
            assert "hooks" in group, event
            assert isinstance(group["hooks"], list), event
            assert group["hooks"], event

            for hook in group["hooks"]:
                assert hook["type"] == "command", event
                assert isinstance(hook["command"], str), event
                assert "/absolute/path/to/examples/" in hook["command"], event
