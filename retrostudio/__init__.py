"""RetroStudio platform-neutral core API."""

from .model import Component, Diagnostic, Entity, Project, Scene, load_project, save_project
from .target import (
    TARGET_API_VERSION,
    BackendDescriptor,
    BackendResult,
    BuildArtifact,
    Capability,
    TargetBackend,
    load_backend,
    negotiate_backend,
)

__all__ = [
    "BackendDescriptor",
    "BackendResult",
    "BuildArtifact",
    "Capability",
    "Component",
    "Diagnostic",
    "Entity",
    "Project",
    "Scene",
    "TARGET_API_VERSION",
    "TargetBackend",
    "load_backend",
    "load_project",
    "negotiate_backend",
    "save_project",
]
