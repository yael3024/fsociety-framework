"""Input validators."""

import ipaddress
from pathlib import Path


def validate_ip(value: str) -> ipaddress.IPv4Address:
    address = ipaddress.ip_address(value)
    if not isinstance(address, ipaddress.IPv4Address):
        raise ValueError("Solo se admite IPv4.")
    return address


def validate_file(path: str | Path) -> Path:
    target = Path(path).expanduser()
    if not target.exists() or not target.is_file():
        raise ValueError(f"No es un archivo regular existente: {target}")
    return target
