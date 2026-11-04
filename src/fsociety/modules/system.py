"""System monitoring facade."""

import platform

from fsociety.platform_adapters.common import connections, processes, system_snapshot


def system_info() -> dict:
    return {"hostname": platform.node(), "os": platform.platform(), "machine": platform.machine(), **system_snapshot()}


def process_inventory() -> list[dict]:
    return processes()


def connection_inventory() -> list[dict]:
    return connections()
