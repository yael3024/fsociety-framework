"""Permission and scope checks for authorized network inventory."""

from __future__ import annotations

import ipaddress
from pathlib import Path

RFC1918_NETWORKS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
)


def _is_rfc1918(network: ipaddress.IPv4Network) -> bool:
    return any(network.subnet_of(private) for private in RFC1918_NETWORKS)


class ScopeError(ValueError):
    """Raised when a requested network is outside the authorized scope."""


def load_scope(path: Path | str) -> list[ipaddress.IPv4Network]:
    networks: list[ipaddress.IPv4Network] = []
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return networks
    for number, line in enumerate(lines, 1):
        value = line.partition("#")[0].strip()
        if not value:
            continue
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError as exc:
            raise ScopeError(f"CIDR inválido en {path}:{number}: {value}") from exc
        if not isinstance(network, ipaddress.IPv4Network) or not _is_rfc1918(network):
            raise ScopeError(f"Solo se permiten redes IPv4 privadas en scope.txt (línea {number})")
        networks.append(network)
    return networks


def authorize_network(value: str, scope_path: Path | str) -> ipaddress.IPv4Network:
    try:
        network = ipaddress.ip_network(value, strict=False)
    except ValueError as exc:
        raise ScopeError(f"Red CIDR inválida: {value}") from exc
    if not isinstance(network, ipaddress.IPv4Network) or not _is_rfc1918(network):
        raise ScopeError("Solo se permiten rangos IPv4 privados.")
    if network.prefixlen < 24:
        raise ScopeError("El rango de escaneo no puede ser mayor que /24.")
    allowed = load_scope(scope_path)
    if not any(network.subnet_of(entry) for entry in allowed):
        raise ScopeError(f"{network} no está registrado en {scope_path}.")
    return network
