"""Read-only file metadata, inventory, and evidence hashing."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path


def hash_file(path: str | Path, algorithm: str = "sha256", chunk_size: int = 1024 * 1024) -> str:
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Algoritmo no disponible: {algorithm}")
    digest = hashlib.new(algorithm)
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_metadata(path: str | Path) -> dict:
    target = Path(path)
    stat = target.stat()
    return {"path": str(target.resolve()), "name": target.name, "size": stat.st_size, "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(), "created_utc": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(), "suffix": target.suffix.lower(), "is_symlink": target.is_symlink()}


def inventory_files(root: str | Path, recursive: bool = True) -> list[dict]:
    base = Path(root).expanduser()
    if not base.exists() or not base.is_dir():
        raise ValueError(f"Directorio inexistente: {base}")
    iterator = base.rglob("*") if recursive else base.iterdir()
    entries = []
    for item in iterator:
        try:
            if item.is_file() and not item.is_symlink():
                entries.append({**file_metadata(item), "relative_path": item.relative_to(base).as_posix(), "sha256": hash_file(item)})
        except (OSError, PermissionError):
            continue
    return sorted(entries, key=lambda item: item["relative_path"].casefold())


def evidence_record(path: str | Path) -> dict:
    metadata = file_metadata(path)
    metadata.update({"sha256": hash_file(path), "sha512": hash_file(path, "sha512"), "recorded_utc": datetime.now(timezone.utc).isoformat()})
    return metadata
