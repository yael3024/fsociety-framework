"""Linux-specific helpers; commands are invoked without a shell."""

from __future__ import annotations

import json
import shutil
import subprocess


def usb_devices() -> list[dict]:
    executable = shutil.which("lsblk")
    if not executable:
        return []
    result = subprocess.run([executable, "--json", "--bytes", "-o", "NAME,TYPE,TRAN,FSTYPE,SIZE,MODEL,MOUNTPOINT"], capture_output=True, text=True, check=False, timeout=10)
    if result.returncode != 0:
        return []
    try:
        devices = json.loads(result.stdout).get("blockdevices", [])
    except json.JSONDecodeError:
        return []
    def flatten(items):
        for item in items:
            if item.get("tran") == "usb":
                yield item
            yield from flatten(item.get("children", []))
    return list(flatten(devices))
