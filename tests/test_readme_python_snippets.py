import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


def _python_blocks(text: str) -> list[str]:
    pattern = re.compile(r"```python\n(.*?)```", re.DOTALL)
    return [m.group(1).strip() for m in pattern.finditer(text)]


def test_readme_python_blocks_exec() -> None:
    content = README.read_text(encoding="utf-8")
    blocks = _python_blocks(content)
    assert blocks, "No python code blocks found in README.md"

    for i, block in enumerate(blocks):
        ns = {"__name__": f"readme_snippet_{i}"}
        exec(block, ns, ns)
