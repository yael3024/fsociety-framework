"""Minimal registry for framework modules."""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    name: str
    description: str
    handler: Callable[..., Any]


class PluginManager:
    def __init__(self) -> None:
        self._modules: dict[str, ModuleInfo] = {}

    def register(self, name: str, description: str, handler: Callable[..., Any]) -> None:
        if name in self._modules:
            raise ValueError(f"Módulo ya registrado: {name}")
        self._modules[name] = ModuleInfo(name, description, handler)

    def get(self, name: str) -> ModuleInfo:
        return self._modules[name]

    def list(self) -> list[ModuleInfo]:
        return list(self._modules.values())
