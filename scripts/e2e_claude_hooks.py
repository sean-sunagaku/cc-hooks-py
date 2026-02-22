#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from shutil import rmtree
from shutil import copy2

ROOT = Path(__file__).resolve().parent.parent


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_settings(tmp: Path, log_hook: Path) -> Path:
    logs_dir = tmp / "logs"
    settings_path = tmp / "claude_settings.json"

    def cmd(event: str) -> str:
        return (
            f"{shlex.quote(sys.executable)} {shlex.quote(str(log_hook))} "
            f"{shlex.quote(str(logs_dir / (event + '.jsonl')))} {shlex.quote(event)}"
        )

    settings = {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup",
                    "hooks": [{"type": "command", "command": cmd("SessionStart")}],
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Read",
                    "hooks": [{"type": "command", "command": cmd("PreToolUse")}],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Read",
                    "hooks": [{"type": "command", "command": cmd("PostToolUse")}],
                }
            ],
            "Stop": [
                {
                    "matcher": "",
                    "hooks": [{"type": "command", "command": cmd("Stop")}],
                }
            ],
        }
    }
    _write_file(settings_path, json.dumps(settings, ensure_ascii=False))
    return settings_path


def _write_log_hook_script(tmp: Path) -> Path:
    hook_script = tmp / "log_hook.py"
    _write_file(
        hook_script,
        """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

log_file = Path(sys.argv[1])
expected_event = sys.argv[2]
raw = sys.stdin.read()

log_file.parent.mkdir(parents=True, exist_ok=True)
with log_file.open('a', encoding='utf-8') as f:
    f.write(raw.strip() + '\\n')

# For PreToolUse, return explicit allow response to keep behavior deterministic.
if expected_event == 'PreToolUse':
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'allow'
        }
    }))
""",
    )
    hook_script.chmod(0o755)
    return hook_script


def _require_claude() -> str | None:
    result = subprocess.run(["bash", "-lc", "command -v claude"], capture_output=True, text=True, check=False)
    path = result.stdout.strip()
    return path or None


def _get_field(payload: dict[str, object], *keys: str) -> object | None:
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def _load_last_json_line(path: Path) -> dict[str, object] | None:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def _validate_payloads(logs_dir: Path) -> tuple[bool, str, dict[str, object]]:
    required = ["SessionStart", "PreToolUse", "PostToolUse", "Stop"]
    report_events: dict[str, dict[str, object]] = {}
    missing: list[str] = []

    for event in required:
        log_file = logs_dir / f"{event}.jsonl"
        event_report: dict[str, object] = {
            "log_file": str(log_file),
            "called": False,
            "entries": 0,
            "json_parse_ok": False,
            "event_name_match": False,
            "tool_name_match": None,
            "errors": [],
        }
        report_events[event] = event_report
        if not log_file.exists():
            event_report["errors"] = ["log_file_missing"]
            missing.append(event)
            continue

        text = log_file.read_text(encoding="utf-8").strip()
        lines = [line for line in text.splitlines() if line.strip()]
        event_report["entries"] = len(lines)
        if lines:
            event_report["called"] = True

        payload = _load_last_json_line(log_file)
        if payload is None:
            event_report["errors"] = ["empty_or_invalid_jsonl"]
            missing.append(event)
            continue
        event_report["json_parse_ok"] = True

        event_name = _get_field(payload, "hook_event_name", "hookEventName")
        if event_name != event:
            event_report["errors"] = [f"hook_event_name_mismatch:{event_name!r}"]
            return (
                False,
                f"{event}: hook_event_name mismatch (got={event_name!r})",
                {"required_events": required, "events": report_events},
            )
        event_report["event_name_match"] = True

        if event == "PreToolUse":
            tool_name = _get_field(payload, "tool_name", "toolName")
            if tool_name != "Read":
                event_report["tool_name_match"] = False
                event_report["errors"] = [f"tool_name_mismatch:{tool_name!r}"]
                return (
                    False,
                    f"PreToolUse: expected tool_name=Read (got={tool_name!r})",
                    {"required_events": required, "events": report_events},
                )
            event_report["tool_name_match"] = True
        elif event == "PostToolUse":
            tool_name = _get_field(payload, "tool_name", "toolName")
            if tool_name != "Read":
                event_report["tool_name_match"] = False
                event_report["errors"] = [f"tool_name_mismatch:{tool_name!r}"]
                return (
                    False,
                    f"PostToolUse: expected tool_name=Read (got={tool_name!r})",
                    {"required_events": required, "events": report_events},
                )
            event_report["tool_name_match"] = True
            tool_response = _get_field(payload, "tool_response", "toolResponse")
            if not isinstance(tool_response, dict):
                event_report["errors"] = ["tool_response_missing_or_not_object"]
                return (
                    False,
                    "PostToolUse: missing tool_response/toolResponse object",
                    {"required_events": required, "events": report_events},
                )
        elif event == "Stop":
            # Stop payload fields may vary by version, so only event name is strictly validated.
            pass

    if missing:
        return (
            False,
            f"missing hook logs: {', '.join(missing)}",
            {"required_events": required, "events": report_events},
        )
    return (
        True,
        "validated hook payloads for SessionStart/PreToolUse/PostToolUse/Stop",
        {"required_events": required, "events": report_events},
    )


def _print_log_summary(logs_dir: Path) -> None:
    events = ["SessionStart", "PreToolUse", "PostToolUse", "Stop"]
    verbose = os.environ.get("E2E_CLAUDE_VERBOSE", "").lower() in {"1", "true", "yes", "on"}
    print(f"[e2e-claude] logs directory: {logs_dir}")
    for event in events:
        path = logs_dir / f"{event}.jsonl"
        if not path.exists():
            print(f"[e2e-claude] {event}: log file missing")
            continue
        text = path.read_text(encoding="utf-8").strip()
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            print(f"[e2e-claude] {event}: log file exists but empty ({path})")
            continue
        preview = lines[-1]
        if not verbose and len(preview) > 600:
            preview = preview[:600] + "...(truncated)"
        print(f"[e2e-claude] {event}: {path} ({len(lines)} entries)")
        print(f"[e2e-claude] {event} last payload: {preview}")


def _persist_run_artifacts(tmp_dir: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_root_env = os.environ.get("E2E_CLAUDE_LOG_DIR")
    base = Path(out_root_env) if out_root_env else (ROOT / ".e2e-logs" / "claude-hooks")
    run_dir = base / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    for name in ["claude_settings.json", "claude.stdout.log", "claude.stderr.log"]:
        src = tmp_dir / name
        if src.exists():
            copy2(src, run_dir / name)

    src_logs = tmp_dir / "logs"
    dst_logs = run_dir / "logs"
    dst_logs.mkdir(parents=True, exist_ok=True)
    if src_logs.exists():
        for item in src_logs.glob("*.jsonl"):
            copy2(item, dst_logs / item.name)
    return run_dir


def _write_validation_report(run_dir: Path, success: bool, message: str, details: dict[str, object]) -> Path:
    report = {
        "success": success,
        "message": message,
        "details": details,
    }
    path = run_dir / "e2e_validation.json"
    _write_file(path, json.dumps(report, ensure_ascii=False, indent=2))
    return path


def _cleanup_old_runs(base: Path) -> None:
    keep_days_raw = os.environ.get("E2E_CLAUDE_KEEP_DAYS", "7")
    try:
        keep_days = int(keep_days_raw)
    except ValueError:
        keep_days = 7

    cutoff = datetime.now(timezone.utc) - timedelta(days=max(0, keep_days))
    if not base.exists():
        return

    for child in base.iterdir():
        if not child.is_dir() or child.name == "_tmp":
            continue
        mtime = datetime.fromtimestamp(child.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            rmtree(child, ignore_errors=True)


def main() -> int:
    claude_path = _require_claude()
    if not claude_path:
        print("[e2e-claude] skip: claude command not found")
        return 0

    base = ROOT / ".e2e-logs" / "claude-hooks"
    _cleanup_old_runs(base)

    tmp = base / "_tmp"
    rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True, exist_ok=True)
    hook_script = _write_log_hook_script(tmp)
    settings_path = _build_settings(tmp, hook_script)

    cmd = [
        claude_path,
        "-p",
        "Read README.md and respond with exactly: E2E_OK",
        "--output-format",
        "json",
        "--settings",
        str(settings_path),
        "--permission-mode",
        "bypassPermissions",
        "--dangerously-skip-permissions",
        "--allowedTools",
        "Read",
    ]

    print("[e2e-claude] running:", " ".join(shlex.quote(x) for x in cmd))
    run = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)
    _write_file(tmp / "claude.stdout.log", run.stdout)
    _write_file(tmp / "claude.stderr.log", run.stderr)

    logs_dir = tmp / "logs"
    _print_log_summary(logs_dir)

    if run.returncode != 0:
        run_dir = _persist_run_artifacts(tmp)
        print("[e2e-claude] claude execution failed")
        print(f"[e2e-claude] artifacts saved: {run_dir}")
        print(run.stdout)
        print(run.stderr)
        return 1

    ok, message, details = _validate_payloads(logs_dir)
    run_dir = _persist_run_artifacts(tmp)
    report_path = _write_validation_report(run_dir, ok, message, details)
    print(f"[e2e-claude] artifacts saved: {run_dir}")
    print(f"[e2e-claude] validation report: {report_path}")
    if not ok:
        print(f"[e2e-claude] validation failed: {message}")
        return 1

    print(f"[e2e-claude] success: {message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
