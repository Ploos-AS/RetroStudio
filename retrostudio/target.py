"""Target backend API for RetroStudio.

M2 defines the host-side plugin contract. Backends are ordinary Python modules
that expose a ``retrostudio_backend()`` factory returning a TargetBackend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Protocol

from .model import Diagnostic, Project

TARGET_API_VERSION = 1


@dataclass(frozen=True)
class Capability:
    id: str
    value: Any = True
    description: str = ""


@dataclass(frozen=True)
class BackendDescriptor:
    id: str
    display_name: str
    backend_version: str
    api_version: int = TARGET_API_VERSION
    capabilities: tuple[Capability, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BuildArtifact:
    kind: str
    path: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BackendResult:
    diagnostics: list[Diagnostic] = field(default_factory=list)
    artifacts: list[BuildArtifact] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(item.level == "error" for item in self.diagnostics)


class TargetBackend(Protocol):
    def describe(self) -> BackendDescriptor: ...

    def validate(self, project: Project, target: str) -> list[Diagnostic]: ...

    def build(self, project: Project, target: str, output_dir: str) -> BackendResult: ...

    def package(self, project: Project, target: str, output_dir: str) -> BackendResult: ...

    def launch(self, project: Project, target: str, artifact: BuildArtifact | None = None) -> BackendResult: ...


def negotiate_backend(backend: TargetBackend) -> BackendDescriptor:
    descriptor = backend.describe()
    if descriptor.api_version != TARGET_API_VERSION:
        raise ValueError(
            f"backend {descriptor.id!r} uses target API {descriptor.api_version}; "
            f"RetroStudio requires {TARGET_API_VERSION}"
        )
    if not descriptor.id:
        raise ValueError("backend id must not be empty")
    return descriptor


def load_backend(module_name: str) -> TargetBackend:
    module = import_module(module_name)
    factory = getattr(module, "retrostudio_backend", None)
    if factory is None or not callable(factory):
        raise ValueError(f"module {module_name!r} does not export retrostudio_backend()")
    backend = factory()
    negotiate_backend(backend)
    return backend
