"""JSON report writer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_report(data: dict[str, Any], data_dir: Path, prefix: str = "report") -> Path:
    target_dir = data_dir / "reports"
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = target_dir / f"{prefix}_{stamp}.json"
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), **data}
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return target
