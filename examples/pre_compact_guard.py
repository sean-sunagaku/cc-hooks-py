#!/usr/bin/env python3
from cc_hooks import PreCompactInput, hook


@hook("PreCompact")
def handle(input: PreCompactInput) -> None:
    # Unknown trigger values are accepted; only known values are typed.
    _ = input.as_known_trigger()
    return None
