from enum import Enum

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - Python < 3.11 compatibility
    class StrEnum(str, Enum):  # type: ignore[no-redef]
        pass


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


class PreCompactTrigger(StrEnum):
    AUTO = "auto"
    MANUAL = "manual"


class SessionStartSource(StrEnum):
    STARTUP = "startup"
    RESUME = "resume"
    CLEAR = "clear"
    COMPACT = "compact"


class SessionEndReason(StrEnum):
    CLEAR = "clear"
    LOGOUT = "logout"
    PROMPT_INPUT_EXIT = "prompt_input_exit"
    OTHER = "other"


class PermissionMode(StrEnum):
    DEFAULT = "default"
    PLAN = "plan"
    ACCEPT_EDITS = "acceptEdits"
    DONT_ASK = "dontAsk"
    BYPASS_PERMISSIONS = "bypassPermissions"


class BuiltinToolName(StrEnum):
    BASH = "Bash"
    WRITE = "Write"
    EDIT = "Edit"
    READ = "Read"
    GLOB = "Glob"
    GREP = "Grep"
    WEB_FETCH = "WebFetch"
    WEB_SEARCH = "WebSearch"
    TASK = "Task"
    NOTEBOOK_EDIT = "NotebookEdit"


class NotificationType(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class ConfigChangeSource(StrEnum):
    USER = "user"
    SYSTEM = "system"
    PROJECT = "project"
