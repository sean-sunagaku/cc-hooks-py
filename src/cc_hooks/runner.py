import asyncio
import inspect
import json
import sys
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel

from cc_hooks.enums import HookEvent
from cc_hooks.models import (
    ConfigChangeInput,
    NotificationInput,
    PermissionRequestInput,
    PostToolUseFailureInput,
    PostToolUseInput,
    PreCompactInput,
    PreToolUseInput,
    SessionEndInput,
    SessionStartInput,
    StopInput,
    SubagentStartInput,
    SubagentStopInput,
    TaskCompletedInput,
    TeammateIdleInput,
    UserPromptSubmitInput,
)

InputModel = type[BaseModel]
Handler = Callable[[Any], BaseModel | None | Awaitable[BaseModel | None]]

_EVENT_INPUT_MODEL: dict[str, InputModel] = {
    HookEvent.SESSION_START.value: SessionStartInput,
    HookEvent.SESSION_END.value: SessionEndInput,
    HookEvent.USER_PROMPT_SUBMIT.value: UserPromptSubmitInput,
    HookEvent.PRE_TOOL_USE.value: PreToolUseInput,
    HookEvent.POST_TOOL_USE.value: PostToolUseInput,
    HookEvent.POST_TOOL_USE_FAILURE.value: PostToolUseFailureInput,
    HookEvent.PERMISSION_REQUEST.value: PermissionRequestInput,
    HookEvent.NOTIFICATION.value: NotificationInput,
    HookEvent.SUBAGENT_START.value: SubagentStartInput,
    HookEvent.SUBAGENT_STOP.value: SubagentStopInput,
    HookEvent.STOP.value: StopInput,
    HookEvent.TEAMMATE_IDLE.value: TeammateIdleInput,
    HookEvent.TASK_COMPLETED.value: TaskCompletedInput,
    HookEvent.CONFIG_CHANGE.value: ConfigChangeInput,
    HookEvent.PRE_COMPACT.value: PreCompactInput,
}


def hook(event: str | HookEvent) -> Callable[[Handler], Handler]:
    resolved_event = event.value if isinstance(event, HookEvent) else event

    def decorator(fn: Handler) -> Handler:
        caller_globals = inspect.stack()[1].frame.f_globals
        if caller_globals.get("__name__") == "__main__":
            _execute(fn, resolved_event)

        return fn

    return decorator


def _resolve_input_model(event: str) -> InputModel:
    if event not in _EVENT_INPUT_MODEL:
        raise ValueError(f"Unsupported hook event: {event}")
    return _EVENT_INPUT_MODEL[event]


def _execute(fn: Handler, event: str) -> None:
    input_model = _resolve_input_model(event)
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw else {}
        parsed_input = input_model(**payload)

        if asyncio.iscoroutinefunction(fn):
            result = asyncio.run(fn(parsed_input))
        else:
            result = fn(parsed_input)

        if result is not None:
            serialized = result.model_dump(by_alias=True, exclude_none=True)
            sys.stdout.write(json.dumps(serialized))

        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        handler_name = getattr(fn, "__name__", "<handler>")
        sys.stderr.write(f"{type(exc).__name__} in event={event} handler={handler_name}: {exc}")
        raise SystemExit(2) from exc
