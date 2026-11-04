"""Windows-specific inventory helpers."""

import platform
import string

import ctypes
import psutil


def windows_version() -> dict[str, str]:
    return {"system": platform.system(), "release": platform.release(), "version": platform.version()}


def usb_drives() -> list[dict]:
    """Return mounted removable drive volumes using the Windows drive API."""
    if platform.system() != "Windows":
        return []
    drive_type = ctypes.windll.kernel32.GetDriveTypeW
    result = []
    partitions = {part.mountpoint.upper(): part for part in psutil.disk_partitions(all=True)}
    for letter in string.ascii_uppercase:
        mountpoint = f"{letter}:\\"
        if drive_type(mountpoint) != 2:  # DRIVE_REMOVABLE
            continue
        try:
            usage = psutil.disk_usage(mountpoint)
        except (OSError, PermissionError):
            continue
        part = partitions.get(mountpoint.upper())
        result.append({"device": part.device if part else mountpoint, "mountpoint": mountpoint, "filesystem": part.fstype if part else "unknown", "size": usage.total, "model": "unavailable"})
    return result
