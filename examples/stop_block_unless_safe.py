#!/usr/bin/env python3
from cc_hooks import StopInput, StopOutput, hook


@hook("Stop")
def handle(input: StopInput) -> StopOutput:
    message = input.last_assistant_message or ""
    if "TODO" in message:
        return StopOutput.block("Please resolve TODO before stopping")
    return StopOutput.ok()
