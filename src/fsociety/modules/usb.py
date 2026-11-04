"""Read-only removable-media inventory and static suspicious-file rules."""

from __future__ import annotations

import platform
from pathlib import Path

import psutil

from fsociety.modules.forensics import hash_file
from fsociety.platform_adapters.linux import usb_devices as linux_usb_devices
from fsociety.platform_adapters.windows import usb_drives as windows_usb_drives

SUSPICIOUS_EXTENSIONS = {".exe", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".lnk", ".hta"}


def usb_inventory() -> list[dict]:
    if platform.system() == "Linux":
        return linux_usb_devices()
    if platform.system() == "Windows":
        return windows_usb_drives()
    return []


def inspect_usb_path(root: str | Path, suspicious_extensions: set[str] | None = None) -> dict:
    base = Path(root).expanduser()
    if not base.is_dir():
        raise ValueError(f"No es un directorio o unidad accesible: {base}")
    extensions = suspicious_extensions or SUSPICIOUS_EXTENSIONS
    files = []
    for path in base.rglob("*"):
        try:
            if path.is_file() and not path.is_symlink():
                suffix = path.suffix.lower()
                files.append({"relative_path": path.relative_to(base).as_posix(), "size": path.stat().st_size, "sha256": hash_file(path), "suspicious": suffix in extensions, "reason": f"extensión {suffix}" if suffix in extensions else None})
        except (OSError, PermissionError):
            continue
    return {"root": str(base.resolve()), "files": files, "suspicious_count": sum(item["suspicious"] for item in files)}
