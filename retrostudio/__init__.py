"""RetroStudio platform-neutral core API."""

from .assets import (
    ASSET_KINDS,
    Asset,
    ContentCache,
    ConversionRequest,
    ResourceUsage,
    budget_diagnostics,
    hash_bytes,
    hash_file,
)
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
    "ASSET_KINDS",
    "Asset",
    "BackendDescriptor",
    "BackendResult",
    "BuildArtifact",
    "Capability",
    "Component",
    "ContentCache",
    "ConversionRequest",
    "Diagnostic",
    "Entity",
    "Project",
    "ResourceUsage",
    "Scene",
    "TARGET_API_VERSION",
    "TargetBackend",
    "budget_diagnostics",
    "hash_bytes",
    "hash_file",
    "load_backend",
    "load_project",
    "negotiate_backend",
    "save_project",
]
