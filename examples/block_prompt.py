#!/usr/bin/env python3
from cc_hooks import UserPromptSubmitInput, UserPromptSubmitOutput, hook


@hook("UserPromptSubmit")
def handle(input: UserPromptSubmitInput) -> UserPromptSubmitOutput:
    if len(input.prompt) > 10000:
        return UserPromptSubmitOutput.block("Prompt too long (max 10000 chars)")
    return UserPromptSubmitOutput.ok()
