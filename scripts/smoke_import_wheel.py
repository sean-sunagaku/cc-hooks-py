#!/usr/bin/env python3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def main() -> int:
    wheels = sorted(DIST.glob("*.whl"))
    if not wheels:
        print("[smoke-import] fail: wheel not found in dist/")
        return 1

    wheel = wheels[-1]
    print(f"[smoke-import] wheel: {wheel}")

    with tempfile.TemporaryDirectory(prefix="cc-hooks-smoke-") as td:
        venv = Path(td) / "venv"
        py = venv / "bin" / "python"

        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        subprocess.run([str(py), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(py), "-m", "pip", "install", str(wheel)], check=True)
        out = subprocess.run(
            [str(py), "-c", "import cc_hooks; print(cc_hooks.__version__)"],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"[smoke-import] imported cc_hooks version={out.stdout.strip()}")

    print("[smoke-import] success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
