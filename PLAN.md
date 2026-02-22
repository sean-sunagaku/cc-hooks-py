# cc-hooks-py - Implementation Spec

## Overview

Claude Code の Hook スクリプトを Python で書くための型定義 + ヘルパーライブラリ。
各 Hook イベントの stdin ペイロードと stdout レスポンスに対応する Pydantic v2 モデルを提供し、
デコレータベースの実行ヘルパーでボイラープレートを排除する。

## Core Decisions

| Item | Decision |
|------|----------|
| Type system | Pydantic v2 (hard dependency) |
| Python version | 3.12+ |
| Helper API | `@hook("EventName")` decorator |
| Event scope | All 15 events |
| Package layout | Modular split by concern |
| Distribution | PyPI (`cc-hooks-py`) + GitHub + uv support |
| Output API | Class methods (`.allow()`, `.deny()`, `.block()`) |
| Error handling | Exit code 2 + stderr (blocking) |
| CLI scaffold | No CLI |
| Execution | Auto-execute at decoration time |
| Stop control | `Output.stop_session(reason)` |
| Async | sync/async 両対応 (asyncio.run()) |
| Tool types | Built-in 10 tools + `register_tool_input()` |
| Versioning | 0.x (0.1.0 start) |
| Extra fields | `extra='allow'` (forward-compatible) |
| Alias strategy | snake_case fields + camelCase alias |
| None return | 許可 (ログ専用フックに便利) |

## Package Structure

```
cc-hooks-py/
├── pyproject.toml
├── LICENSE                    # MIT (existing)
├── README.md
├── src/
│   └── cc_hooks/
│       ├── __init__.py        # re-exports: hook, all Input/Output models, register_tool_input
│       ├── py.typed            # PEP 561 marker
│       ├── enums.py            # HookEvent, PermissionDecision, etc.
│       ├── runner.py           # @hook decorator, stdin/stdout handling, asyncio detection
│       ├── registry.py         # register_tool_input() + built-in tool registry
│       ├── models/
│       │   ├── __init__.py     # re-exports all models
│       │   ├── _base.py        # BaseInput, BaseOutput (common fields)
│       │   ├── session_start.py
│       │   ├── session_end.py
│       │   ├── user_prompt_submit.py
│       │   ├── pre_tool_use.py
│       │   ├── post_tool_use.py
│       │   ├── post_tool_use_failure.py
│       │   ├── permission_request.py
│       │   ├── notification.py
│       │   ├── subagent_start.py
│       │   ├── subagent_stop.py
│       │   ├── stop.py
│       │   ├── teammate_idle.py
│       │   ├── task_completed.py
│       │   ├── config_change.py
│       │   └── pre_compact.py
│       └── tools/
│           ├── __init__.py     # re-exports all tool input models
│           ├── bash.py         # BashInput
│           ├── write.py        # WriteInput
│           ├── edit.py         # EditInput
│           ├── read.py         # ReadInput
│           ├── glob.py         # GlobInput
│           ├── grep.py         # GrepInput
│           ├── web_fetch.py    # WebFetchInput
│           ├── web_search.py   # WebSearchInput
│           ├── task.py         # TaskInput
│           └── notebook_edit.py # NotebookEditInput
├── tests/
│   ├── conftest.py
│   ├── test_models/
│   │   ├── test_pre_tool_use.py
│   │   ├── test_post_tool_use.py
│   │   └── ... (per event)
│   ├── test_runner.py
│   ├── test_registry.py
│   └── test_tools/
│       └── test_bash.py
└── examples/
    ├── deny_bash_rm.py
    ├── log_tool_usage.py
    ├── block_prompt.py
    └── async_slack_notify.py
```

## Detailed Design

### 1. Enums (`cc_hooks/enums.py`)

```python
from enum import StrEnum

class HookEvent(StrEnum):
    SESSION_START = "SessionStart"
    SESSION_END = "SessionEnd"
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    POST_TOOL_USE_FAILURE = "PostToolUseFailure"
    PERMISSION_REQUEST = "PermissionRequest"
    NOTIFICATION = "Notification"
    SUBAGENT_START = "SubagentStart"
    SUBAGENT_STOP = "SubagentStop"
    STOP = "Stop"
    TEAMMATE_IDLE = "TeammateIdle"
    TASK_COMPLETED = "TaskCompleted"
    CONFIG_CHANGE = "ConfigChange"
    PRE_COMPACT = "PreCompact"

class PermissionDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"
```

### 2. Base Models (`cc_hooks/models/_base.py`)

```python
from pydantic import BaseModel, ConfigDict

class BaseInput(BaseModel):
    model_config = ConfigDict(
        extra="allow",               # forward-compatible with future Claude Code fields
        populate_by_name=True,        # accept both camelCase and snake_case
    )

    session_id: str
    transcript_path: str = Field(alias="transcript_path")
    cwd: str
    permission_mode: str = Field(alias="permission_mode")
    hook_event_name: str = Field(alias="hook_event_name")

class BaseOutput(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        exclude_none=True,
        populate_by_name=True,        # accept both camelCase and snake_case
    )

    # Universal fields
    continue_: bool | None = Field(None, alias="continue")
    stop_reason: str | None = Field(None, alias="stopReason")
    suppress_output: bool | None = Field(None, alias="suppressOutput")
    system_message: str | None = Field(None, alias="systemMessage")

    @classmethod
    def stop_session(cls, reason: str) -> Self:
        """Stop Claude's entire processing. Use with caution."""
        return cls(continue_=False, stop_reason=reason)
```

### 3. Event-Specific Input Models (examples)

#### PreToolUseInput (`cc_hooks/models/pre_tool_use.py`)

```python
class PreToolUseInput(BaseInput):
    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str

    def as_bash_input(self) -> BashInput | None:
        """Parse tool_input as BashInput if tool_name is 'Bash'."""
        if self.tool_name == "Bash":
            return BashInput(**self.tool_input)
        return None

    def as_tool_input[T: BaseModel](self, model: type[T]) -> T | None:
        """Parse tool_input as a custom Pydantic model."""
        try:
            return model(**self.tool_input)
        except ValidationError:
            return None

    # Convenience methods for each built-in tool
    def as_write_input(self) -> WriteInput | None: ...
    def as_edit_input(self) -> EditInput | None: ...
    def as_read_input(self) -> ReadInput | None: ...
    # ... etc
```

#### PostToolUseInput (`cc_hooks/models/post_tool_use.py`)

```python
class PostToolUseInput(BaseInput):
    tool_name: str
    tool_input: dict[str, Any]
    tool_response: dict[str, Any]  # Varies by tool
    tool_use_id: str

    # Same as_*_input() helpers as PreToolUseInput
```

### 4. Event-Specific Output Models (examples)

#### PreToolUseOutput

```python
class PreToolUseHookSpecific(BaseModel):
    hook_event_name: Literal["PreToolUse"] = "PreToolUse"
    permission_decision: PermissionDecision | None = Field(None, alias="permissionDecision")
    permission_decision_reason: str | None = Field(None, alias="permissionDecisionReason")
    updated_input: dict[str, Any] | None = Field(None, alias="updatedInput")
    additional_context: str | None = Field(None, alias="additionalContext")

class PreToolUseOutput(BaseOutput):
    hook_specific_output: PreToolUseHookSpecific | None = Field(None, alias="hookSpecificOutput")

    @classmethod
    def allow(cls) -> Self:
        return cls(hook_specific_output=PreToolUseHookSpecific(
            permission_decision=PermissionDecision.ALLOW
        ))

    @classmethod
    def deny(cls, reason: str) -> Self:
        return cls(hook_specific_output=PreToolUseHookSpecific(
            permission_decision=PermissionDecision.DENY,
            permission_decision_reason=reason
        ))

    @classmethod
    def ask(cls, reason: str) -> Self:
        return cls(hook_specific_output=PreToolUseHookSpecific(
            permission_decision=PermissionDecision.ASK,
            permission_decision_reason=reason
        ))

    @classmethod
    def modify(cls, updated_input: dict[str, Any], reason: str | None = None) -> Self:
        return cls(hook_specific_output=PreToolUseHookSpecific(
            permission_decision=PermissionDecision.ALLOW,
            updated_input=updated_input,
            permission_decision_reason=reason
        ))

    @classmethod
    def add_context(cls, context: str) -> Self:
        return cls(hook_specific_output=PreToolUseHookSpecific(
            additional_context=context
        ))
```

#### StopOutput / PostToolUseOutput (decision-based pattern)

```python
class StopOutput(BaseOutput):
    decision: str | None = None
    reason: str | None = None

    @classmethod
    def ok(cls) -> Self:
        return cls()

    @classmethod
    def block(cls, reason: str) -> Self:
        return cls(decision="block", reason=reason)
```

### 5. Runner / Decorator (`cc_hooks/runner.py`)

```python
import sys
import json
import asyncio
import inspect

def hook(event: str | HookEvent):
    """Decorator that handles stdin parsing, handler execution, and JSON output."""
    def decorator(fn):
        # Check if called from __main__
        frame = inspect.stack()[1]
        caller_globals = frame[0].f_globals

        if caller_globals.get("__name__") == "__main__":
            _execute(fn, event)

        return fn
    return decorator

def _execute(fn, event: str):
    input_model = _resolve_input_model(event)

    try:
        raw = json.loads(sys.stdin.read())
        parsed_input = input_model(**raw)

        if asyncio.iscoroutinefunction(fn):
            result = asyncio.run(fn(parsed_input))
        else:
            result = fn(parsed_input)

        if result is not None:
            output_json = result.model_dump(by_alias=True, exclude_none=True)
            sys.stdout.write(json.dumps(output_json))

        sys.exit(0)

    except Exception as e:
        sys.stderr.write(f"{type(e).__name__}: {e}")
        sys.exit(2)
```

### 6. Tool Registry (`cc_hooks/registry.py`)

```python
_tool_registry: dict[str, type[BaseModel]] = {}

def register_tool_input(tool_name: str, model: type[BaseModel]) -> None:
    """Register a custom Pydantic model for a tool's input schema."""
    _tool_registry[tool_name] = model

def get_tool_input_model(tool_name: str) -> type[BaseModel] | None:
    """Get the registered model for a tool name."""
    return _tool_registry.get(tool_name)

# Built-in tools are pre-registered at import time
def _register_builtins():
    register_tool_input("Bash", BashInput)
    register_tool_input("Write", WriteInput)
    register_tool_input("Edit", EditInput)
    register_tool_input("Read", ReadInput)
    register_tool_input("Glob", GlobInput)
    register_tool_input("Grep", GrepInput)
    register_tool_input("WebFetch", WebFetchInput)
    register_tool_input("WebSearch", WebSearchInput)
    register_tool_input("Task", TaskInput)
    register_tool_input("NotebookEdit", NotebookEditInput)
```

### 7. Tool Input Models (`cc_hooks/tools/`)

```python
# cc_hooks/tools/bash.py
class BashInput(BaseModel):
    command: str
    description: str | None = None
    timeout: int | None = None
    run_in_background: bool | None = None

# cc_hooks/tools/write.py
class WriteInput(BaseModel):
    file_path: str
    content: str

# cc_hooks/tools/edit.py
class EditInput(BaseModel):
    file_path: str
    old_string: str
    new_string: str
    replace_all: bool = False

# cc_hooks/tools/read.py
class ReadInput(BaseModel):
    file_path: str
    offset: int | None = None
    limit: int | None = None

# ... etc
```

### 8. Public API (`cc_hooks/__init__.py`)

```python
# Decorator
from cc_hooks.runner import hook

# Registry
from cc_hooks.registry import register_tool_input

# All Input models
from cc_hooks.models import (
    SessionStartInput, SessionStartOutput,
    SessionEndInput, SessionEndOutput,
    UserPromptSubmitInput, UserPromptSubmitOutput,
    PreToolUseInput, PreToolUseOutput,
    PostToolUseInput, PostToolUseOutput,
    PostToolUseFailureInput, PostToolUseFailureOutput,
    PermissionRequestInput, PermissionRequestOutput,
    NotificationInput, NotificationOutput,
    SubagentStartInput, SubagentStartOutput,
    SubagentStopInput, SubagentStopOutput,
    StopInput, StopOutput,
    TeammateIdleInput, TeammateIdleOutput,
    TaskCompletedInput, TaskCompletedOutput,
    ConfigChangeInput, ConfigChangeOutput,
    PreCompactInput, PreCompactOutput,
)

# Tool input models
from cc_hooks.tools import (
    BashInput, WriteInput, EditInput, ReadInput,
    GlobInput, GrepInput, WebFetchInput, WebSearchInput,
    TaskInput, NotebookEditInput,
)

# Enums
from cc_hooks.enums import HookEvent, PermissionDecision
```

## All 15 Event Input/Output Schemas

### Common Input Fields (all events)

| Field | Type | Description |
|-------|------|-------------|
| session_id | str | Session identifier |
| transcript_path | str | Path to conversation JSONL |
| cwd | str | Current working directory |
| permission_mode | str | "default" / "plan" / "acceptEdits" / "dontAsk" / "bypassPermissions" |
| hook_event_name | str | Event name |

### Event-Specific Fields

| Event | Extra Input Fields | Output Pattern |
|-------|-------------------|----------------|
| SessionStart | source, model, agent_type? | hookSpecificOutput.additionalContext |
| SessionEnd | reason | No decision control |
| UserPromptSubmit | prompt | decision/reason + hookSpecificOutput.additionalContext |
| PreToolUse | tool_name, tool_input, tool_use_id | hookSpecificOutput (permissionDecision, updatedInput, additionalContext) |
| PostToolUse | tool_name, tool_input, tool_response, tool_use_id | decision/reason + hookSpecificOutput.additionalContext + updatedMCPToolOutput? |
| PostToolUseFailure | tool_name, tool_input, tool_use_id, error, is_interrupt? | hookSpecificOutput.additionalContext |
| PermissionRequest | tool_name, tool_input, permission_suggestions? | hookSpecificOutput.decision (behavior, updatedInput, message) |
| Notification | message, title?, notification_type | No decision control |
| SubagentStart | agent_id, agent_type | No decision control |
| SubagentStop | stop_hook_active, agent_id, agent_type, agent_transcript_path, last_assistant_message | decision/reason |
| Stop | stop_hook_active, last_assistant_message | decision/reason |
| TeammateIdle | teammate_name, team_name | Exit code 2 only |
| TaskCompleted | task_id, task_subject, task_description?, teammate_name?, team_name? | Exit code 2 only |
| ConfigChange | source, file_path? | decision/reason |
| PreCompact | trigger, custom_instructions | No decision control |

## Usage Examples

### Example 1: Deny dangerous bash commands

```python
#!/usr/bin/env python3
from cc_hooks import hook, PreToolUseInput, PreToolUseOutput

@hook("PreToolUse")
def handle(input: PreToolUseInput) -> PreToolUseOutput:
    bash = input.as_bash_input()
    if bash and ("rm -rf" in bash.command or "sudo" in bash.command):
        return PreToolUseOutput.deny(f"Dangerous command blocked: {bash.command}")
    return PreToolUseOutput.allow()
```

### Example 2: Log tool usage (async, PostToolUse)

```python
#!/usr/bin/env python3
import httpx
from cc_hooks import hook, PostToolUseInput, PostToolUseOutput

@hook("PostToolUse")
async def handle(input: PostToolUseInput) -> PostToolUseOutput:
    async with httpx.AsyncClient() as client:
        await client.post("https://hooks.slack.com/...", json={
            "text": f"Tool {input.tool_name} used in {input.cwd}"
        })
    return PostToolUseOutput.ok()
```

### Example 3: Block prompts with custom validation

```python
#!/usr/bin/env python3
from cc_hooks import hook, UserPromptSubmitInput, UserPromptSubmitOutput

@hook("UserPromptSubmit")
def handle(input: UserPromptSubmitInput) -> UserPromptSubmitOutput:
    if len(input.prompt) > 10000:
        return UserPromptSubmitOutput.block("Prompt too long (max 10000 chars)")
    return UserPromptSubmitOutput.ok()
```

### Example 4: Custom MCP tool type

```python
#!/usr/bin/env python3
from pydantic import BaseModel
from cc_hooks import hook, register_tool_input, PreToolUseInput, PreToolUseOutput

class SlackPostInput(BaseModel):
    channel: str
    text: str

register_tool_input("mcp__slack__post_message", SlackPostInput)

@hook("PreToolUse")
def handle(input: PreToolUseInput) -> PreToolUseOutput:
    slack = input.as_tool_input(SlackPostInput)
    if slack and slack.channel == "#production":
        return PreToolUseOutput.deny("Cannot post to #production")
    return PreToolUseOutput.allow()
```

## Build & Distribution

### pyproject.toml

```toml
[project]
name = "cc-hooks-py"
version = "0.1.0"
description = "Type-safe Python library for Claude Code hooks"
readme = "README.md"
license = "MIT"
requires-python = ">=3.12"
dependencies = ["pydantic>=2.0,<3.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24", "ruff>=0.8", "mypy>=1.13"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cc_hooks"]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_PROJECT_DIR` | Project root directory |
| `CLAUDE_PLUGIN_ROOT` | Plugin root (for plugin hooks) |
| `CLAUDE_CODE_REMOTE` | "true" in remote environments |
| `CLAUDE_ENV_FILE` | Env file path (SessionStart only) |

## Testing Strategy

- **pytest** with inline fixtures
- **pytest-asyncio** for async handler tests
- Test each model's serialization/deserialization
- Test convenience methods (`.allow()`, `.deny()`, `.block()`, etc.)
- Test runner with mock stdin/stdout
- Test error handling (exit code 2)
- Test custom tool registration
- Test async/sync handler detection

## Testability

`@hook` デコレータは関数をそのまま返す。`__main__` チェックにより、import 時には実行されない。

```python
# hook_script.py
@hook("PreToolUse")
def handle(input: PreToolUseInput) -> PreToolUseOutput:
    bash = input.as_bash_input()
    if bash and "rm -rf" in bash.command:
        return PreToolUseOutput.deny("Dangerous")
    return PreToolUseOutput.allow()

# test_hook_script.py
from hook_script import handle  # auto-execute されない

def test_deny_rm():
    mock = PreToolUseInput(
        session_id="test",
        transcript_path="/tmp/test.jsonl",
        cwd="/tmp",
        permission_mode="default",
        hook_event_name="PreToolUse",
        tool_name="Bash",
        tool_input={"command": "rm -rf /"},
        tool_use_id="toolu_test",
    )
    result = handle(mock)
    assert result.hook_specific_output.permission_decision == "deny"
```

### None Return (ログ専用フック)

```python
@hook("PostToolUse")
def handle(input: PostToolUseInput) -> None:
    # ログだけ取って何も返さない → stdout 空、exit(0)
    with open("/tmp/hook.log", "a") as f:
        f.write(f"{input.tool_name}\n")
```

## Implementation Order

1. `enums.py` - Enum definitions
2. `models/_base.py` - BaseInput, BaseOutput
3. `tools/*.py` - Tool input models (10 tools)
4. `registry.py` - Tool registry + register_tool_input()
5. `models/*.py` - All 15 event Input/Output models
6. `runner.py` - @hook decorator
7. `__init__.py` - Public API re-exports
8. `pyproject.toml` - Build configuration
9. `tests/` - Test suite
10. `examples/` - Example hook scripts
