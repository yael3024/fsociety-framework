"""Portable SHA-256 baselines with root-relative paths."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fsociety.modules.forensics import hash_file


def create_baseline(root: str | Path, output: str | Path | None = None) -> dict:
    base = Path(root).expanduser().resolve()
    if not base.is_dir():
        raise ValueError(f"No es un directorio: {base}")
    files = {}
    for item in base.rglob("*"):
        try:
            if item.is_file() and not item.is_symlink():
                files[item.relative_to(base).as_posix()] = hash_file(item)
        except OSError:
            continue
    baseline = {"version": 1, "root_name": base.name, "created_utc": datetime.now(timezone.utc).isoformat(), "algorithm": "sha256", "files": dict(sorted(files.items()))}
    if output:
        Path(output).write_text(json.dumps(baseline, indent=2, ensure_ascii=False), encoding="utf-8")
    return baseline


def check_integrity(root: str | Path, baseline: str | Path | dict) -> dict:
    base = Path(root).expanduser().resolve()
    expected = json.loads(Path(baseline).read_text(encoding="utf-8")) if isinstance(baseline, (str, Path)) else baseline
    if expected.get("algorithm") != "sha256" or not isinstance(expected.get("files"), dict):
        raise ValueError("Formato de línea base no válido.")
    current = {}
    for item in base.rglob("*"):
        try:
            if item.is_file() and not item.is_symlink():
                current[item.relative_to(base).as_posix()] = hash_file(item)
        except OSError:
            continue
    original = expected["files"]
    names = set(original) | set(current)
    modified = sorted(name for name in names & original.keys() & current.keys() if original[name] != current[name])
    return {"root": str(base), "modified": modified, "new": sorted(current.keys() - original.keys()), "deleted": sorted(original.keys() - current.keys()), "unchanged": sorted(name for name in names & original.keys() & current.keys() if original[name] == current[name]), "ok": original.keys() == current.keys() and not modified}
