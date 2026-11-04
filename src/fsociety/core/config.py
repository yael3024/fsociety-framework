"""Central configuration loading with safe defaults."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Settings:
    data_dir: Path = Path("data")
    scope_file: Path = Path("config/scope.txt")
    log_level: str = "INFO"
    report_format: str = "json"
    network_timeout: float = 0.5
    network_ports: list[int] = field(default_factory=lambda: [22, 53, 80, 443, 445, 3389])
    suspicious_extensions: list[str] = field(default_factory=lambda: [".exe", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".lnk"])

    @classmethod
    def load(cls, path: Path | str = "config/settings.json") -> "Settings":
        config_path = Path(path)
        if not config_path.exists():
            return cls()
        try:
            raw: dict[str, Any] = json.loads(config_path.read_text(encoding="utf-8"))
            allowed = {item.name for item in cls.__dataclass_fields__.values()}
            values = {key: value for key, value in raw.items() if key in allowed}
            for key in ("data_dir", "scope_file"):
                if key in values:
                    values[key] = Path(values[key])
            return cls(**values)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValueError(f"No se pudo cargar la configuración {config_path}: {exc}") from exc

    def initialize(self) -> None:
        for name in ("logs", "reports", "evidence"):
            (self.data_dir / name).mkdir(parents=True, exist_ok=True)
