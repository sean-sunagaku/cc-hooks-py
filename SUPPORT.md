# Support Policy

## Supported Python Versions

- Primary support: Python 3.12+
- CI also validates 3.13 for quality checks.

## Compatibility Policy

- While in `0.x`, breaking changes may be introduced in minor releases.
- Patch releases (`0.y.z`) should remain backward-compatible whenever possible.

## Deprecation Policy

- Deprecated APIs are announced in `CHANGELOG.md` before removal when possible.
- Removal may happen in a future minor release during `0.x`.

## Reporting Issues

Please open an issue with:

- minimal reproducible payload
- expected vs actual behavior
- environment details (`python`, `cc-hooks-py`, `Claude Code` versions)
