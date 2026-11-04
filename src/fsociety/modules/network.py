"""Conservative TCP host inventory for authorized private ranges."""

from __future__ import annotations

import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from fsociety.core.permissions import authorize_network

COMMON_SERVICES = {22: "ssh", 53: "domain", 80: "http", 443: "https", 445: "microsoft-ds", 3389: "ms-wbt-server"}


def scan_network(cidr: str, scope_path: Path | str, ports: list[int] | None = None, timeout: float = 0.5, workers: int = 64) -> dict:
    network = authorize_network(cidr, scope_path)
    ports = ports or [22, 53, 80, 443, 445, 3389]
    if any(not 1 <= port <= 65535 for port in ports):
        raise ValueError("Los puertos deben estar entre 1 y 65535.")
    if not 0 < timeout <= 3:
        raise ValueError("El timeout debe estar entre 0 y 3 segundos.")
    if not 1 <= workers <= 64:
        raise ValueError("El número de workers debe estar entre 1 y 64.")

    def probe(address: ipaddress.IPv4Address) -> dict | None:
        host = {"ip": str(address), "reachable": False, "open_ports": []}
        for port in ports:
            try:
                with socket.create_connection((str(address), port), timeout=timeout):
                    host["open_ports"].append({"port": port, "service": COMMON_SERVICES.get(port, "unknown")})
            except (OSError, TimeoutError):
                continue
        host["reachable"] = bool(host["open_ports"])
        return host if host["reachable"] else None

    found = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(probe, address) for address in network.hosts()]
        for future in as_completed(futures):
            item = future.result()
            if item:
                found.append(item)
    return {"network": str(network), "hosts_scanned": sum(1 for _ in network.hosts()), "hosts_found": sorted(found, key=lambda item: ipaddress.ip_address(item["ip"]))}
