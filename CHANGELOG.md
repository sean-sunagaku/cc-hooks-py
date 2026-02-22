# Changelog

All notable changes to this project will be documented in this file.

## Versioning Policy (0.x)

- This project follows SemVer-style versioning while in `0.x`.
- `0.y.0` may include breaking API changes.
- `0.y.z` is for backward-compatible fixes and small improvements.
- We aim to keep public API breakage explicit in release notes.

## [0.1.0] - 2026-02-22

### Added
- Initial `cc-hooks-py` package structure.
- Pydantic models for all 15 Claude Code hook events.
- Built-in tool input models and custom tool registry support.
- `@hook` decorator runner for sync/async handlers.
- Unit tests for models, registry, tools, and runner.
- CI workflow for lint/typecheck/test and package validation.
- Makefile targets for local quality checks and packaging.
