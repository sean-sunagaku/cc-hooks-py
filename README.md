# cc-hooks-py

Type-safe Python library for Claude Code Hooks using Pydantic v2.

- Supports all 15 hook events
- `@hook("EventName")` decorator with sync/async support
- Built-in tool input models + custom tool registration
- Forward-compatible input handling (`extra='allow'`)

> Stability note: while the project is in `0.x`, minor releases may include breaking changes.

## Requirements

- Python 3.12+
- PEP 561 typing support is included (`py.typed` bundled)

## Install

```bash
pip install cc-hooks-py
```

For development:

```bash
make venv
make install
```

## Quick Start

```python
from cc_hooks import PreToolUseInput, PreToolUseOutput, hook

@hook("PreToolUse")
def handle(input: PreToolUseInput) -> PreToolUseOutput:
    bash = input.as_bash_input()
    if bash and "rm -rf" in bash.command:
        return PreToolUseOutput.deny("Dangerous command blocked")
    return PreToolUseOutput.allow()
```

## Minimal Event Samples

### SessionStart

```python
from cc_hooks import SessionStartInput, SessionStartOutput, hook

@hook("SessionStart")
def handle(input: SessionStartInput) -> SessionStartOutput:
    return SessionStartOutput.add_context(f"Started from {input.source}")
```

### PreToolUse

```python
from cc_hooks import PreToolUseInput, PreToolUseOutput, hook

@hook("PreToolUse")
def handle(input: PreToolUseInput) -> PreToolUseOutput:
    return PreToolUseOutput.allow()
```

### PostToolUse

```python
from cc_hooks import PostToolUseInput, PostToolUseOutput, hook

@hook("PostToolUse")
def handle(input: PostToolUseInput) -> PostToolUseOutput:
    return PostToolUseOutput.ok()
```

### UserPromptSubmit

```python
from cc_hooks import UserPromptSubmitInput, UserPromptSubmitOutput, hook

@hook("UserPromptSubmit")
def handle(input: UserPromptSubmitInput) -> UserPromptSubmitOutput:
    if len(input.prompt) > 10_000:
        return UserPromptSubmitOutput.block("Prompt too long")
    return UserPromptSubmitOutput.ok()
```

### PreCompact

```python
from cc_hooks import PreCompactInput, hook

@hook("PreCompact")
def handle(input: PreCompactInput) -> None:
    known = input.as_known_trigger()
    if known is None:
        # unknown trigger is allowed
        return None
```

### Stop

```python
from cc_hooks import StopInput, StopOutput, hook

@hook("Stop")
def handle(input: StopInput) -> StopOutput:
    return StopOutput.block("Please add tests before stopping")
```

## Custom MCP Tool Registration

```python
from pydantic import BaseModel
from cc_hooks import PreToolUseInput, PreToolUseOutput, hook, register_tool_input

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

## Error Handling Behavior

- Unhandled exception in hook handler:
  - writes `<ExceptionType>: <message>` to `stderr`
  - exits with code `2` (blocking)
- Returning `None`:
  - writes nothing to `stdout`
  - exits with code `0`

## Compatibility Policy for Future Values

Some fields may get new values from Claude Code over time.

Policy:

- Raw fields remain permissive (`str`) to accept unknown values.
- `as_known_*()` helpers try mapping to enums.
- Unknown values are not rejected; helper returns `None`.

Examples:

- `PreCompactInput.as_known_trigger()`
- `SessionStartInput.as_known_source()`
- `SessionEndInput.as_known_reason()`
- `BaseInput.as_known_permission_mode()`
- `ToolInputParsingMixin.as_builtin_tool_name()`
- `NotificationInput.as_known_notification_type()`
- `ConfigChangeInput.as_known_source()`

## Running Checks

```bash
make check
make package-check
make release-readiness
make release-check
make e2e-claude
make e2e-claude-verbose
```

`make e2e-claude` writes hook invocation logs under `.e2e-logs/claude-hooks/<timestamp>/logs/`.
`make e2e-claude-verbose` prints full payload content to stdout (no truncation).

## Version Management

Use hatch-backed version management (single source: `src/cc_hooks/__about__.py`):

```bash
make version
make bump-patch
# or: make bump-minor / make bump-major
```

## Publish Workflows

- `publish.yml` runs on:
  - tag push `v*` (publishes to PyPI when `PYPI_API_TOKEN` is configured)
  - manual dispatch (`target=testpypi|pypi|testpypi-oidc|pypi-oidc`)
- For TestPyPI manual publish, set repository secret:
  - `TEST_PYPI_API_TOKEN`
- For Trusted Publishing (OIDC), configure PyPI/TestPyPI trusted publisher and run with `*-oidc` targets.

## Claude Hook-like Local Simulation

You can run example hooks with sample payloads locally:

```bash
python examples/simulate_claude_hooks.py
```

It executes:

- `SessionStart`
- `PreToolUse`
- `PostToolUse`
- `UserPromptSubmit`
- `PreCompact`
- `Stop`

including cases with unexpected payload fields.

## Example Claude Hook Configuration (snippet)

See `/Users/babashunsuke/Repository/cc-hooks-py/examples/claude_hooks_settings.json` for a sample mapping.
