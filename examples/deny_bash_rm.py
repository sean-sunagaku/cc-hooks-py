#!/usr/bin/env python3
from cc_hooks import PreToolUseInput, PreToolUseOutput, hook


@hook("PreToolUse")
def handle(input: PreToolUseInput) -> PreToolUseOutput:
    bash = input.as_bash_input()
    if bash and "rm -rf" in bash.command:
        return PreToolUseOutput.deny(f"Dangerous command blocked: {bash.command}")
    return PreToolUseOutput.allow()
