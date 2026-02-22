#!/usr/bin/env python3
from cc_hooks import PostToolUseInput, hook


@hook("PostToolUse")
def handle(input: PostToolUseInput) -> None:
    with open("/tmp/hook.log", "a", encoding="utf-8") as f:
        f.write(f"{input.tool_name}\n")
