"""Operating system identification."""

import platform


def platform_info() -> dict[str, str]:
    system = platform.system()
    release = platform.release()
    name = platform.platform()
    if system == "Windows":
        family = "Windows 10/11" if release in {"10", "11"} or release.startswith("10.") else "Windows"
    elif system == "Linux":
        try:
            os_release = open("/etc/os-release", encoding="utf-8").read().lower()
        except OSError:
            os_release = ""
        family = "Kali Linux" if "kali" in os_release else "Arch Linux" if "arch" in os_release else "Linux"
    else:
        family = system or "Unknown"
    return {"system": system, "release": release, "family": family, "platform": name}
