#!/usr/bin/env python3
from cc_hooks import SessionStartInput, SessionStartOutput, hook


@hook("SessionStart")
def handle(input: SessionStartInput) -> SessionStartOutput:
    source = input.as_known_source()
    if source is None:
        return SessionStartOutput.add_context(f"Session started (source={input.source})")
    return SessionStartOutput.add_context(f"Session started from {source.value}")
