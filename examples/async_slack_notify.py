#!/usr/bin/env python3
import httpx

from cc_hooks import PostToolUseInput, PostToolUseOutput, hook


@hook("PostToolUse")
async def handle(input: PostToolUseInput) -> PostToolUseOutput:
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://hooks.slack.com/services/your/slack/webhook",
            json={"text": f"Tool {input.tool_name} used in {input.cwd}"},
        )
    return PostToolUseOutput.ok()
