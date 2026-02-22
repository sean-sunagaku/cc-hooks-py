import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_all_python_files_compile() -> None:
    excluded_parts = {".venv312", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".e2e-logs"}
    files = [
        p
        for p in ROOT.rglob("*.py")
        if not any(part in excluded_parts for part in p.parts)
    ]

    assert files, "No Python files found"
    for path in files:
        py_compile.compile(str(path), doraise=True)
