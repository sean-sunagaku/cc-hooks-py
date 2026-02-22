#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    about = ROOT / "src" / "cc_hooks" / "__about__.py"
    changelog = ROOT / "CHANGELOG.md"

    about_text = about.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', about_text)
    if not m:
        print("[release-readiness] fail: version not found in __about__.py")
        return 1

    version = m.group(1)
    changelog_text = changelog.read_text(encoding="utf-8")

    if f"## [{version}]" not in changelog_text:
        print(f"[release-readiness] fail: CHANGELOG.md missing heading for [{version}]")
        return 1

    print(f"[release-readiness] success: version {version} is present in CHANGELOG.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
