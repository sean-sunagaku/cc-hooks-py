#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

import cc_hooks.models as models_mod
import cc_hooks.tools as tools_mod

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "schemas"


def _iter_model_classes(module: Any):
    for name in getattr(module, "__all__", []):
        obj = getattr(module, name, None)
        if isinstance(obj, type) and issubclass(obj, BaseModel):
            yield name, obj


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    model_dir = OUT / "models"
    tool_dir = OUT / "tools"
    model_dir.mkdir(parents=True, exist_ok=True)
    tool_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for name, cls in _iter_model_classes(models_mod):
        path = model_dir / f"{name}.schema.json"
        path.write_text(json.dumps(cls.model_json_schema(by_alias=True), ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1

    for name, cls in _iter_model_classes(tools_mod):
        path = tool_dir / f"{name}.schema.json"
        path.write_text(json.dumps(cls.model_json_schema(by_alias=True), ensure_ascii=False, indent=2), encoding="utf-8")
        count += 1

    print(f"[schema] generated {count} schema files under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
