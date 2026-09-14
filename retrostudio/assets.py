"""Platform-neutral asset pipeline primitives for RetroStudio.

RetroStudio owns source-asset identity, hashing, cache keys, conversion requests
and generic resource-budget diagnostics. Target-specific conversion remains in
AmiStudio, AtariStudio, or another backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

from .model import Diagnostic

ASSET_KINDS = frozenset({"image", "palette", "tilemap", "audio"})


@dataclass(frozen=True)
class Asset:
    asset_id: str
    kind: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        if not self.asset_id:
            diagnostics.append(Diagnostic("error", "asset.id_empty", "asset_id must not be empty", self.source))
        if self.kind not in ASSET_KINDS:
            diagnostics.append(
                Diagnostic("error", "asset.kind_unknown", f"unsupported asset kind: {self.kind}", self.source)
            )
        if not self.source:
            diagnostics.append(Diagnostic("error", "asset.source_empty", "asset source must not be empty", self.asset_id))
        return diagnostics


@dataclass(frozen=True)
class ConversionRequest:
    asset: Asset
    target: str
    operation: str = "convert"
    options: dict[str, Any] = field(default_factory=dict)

    def cache_key(self, source_digest: str, backend_id: str, backend_version: str) -> str:
        payload = {
            "asset_id": self.asset.asset_id,
            "kind": self.asset.kind,
            "source_digest": source_digest,
            "target": self.target,
            "operation": self.operation,
            "options": self.options,
            "backend_id": backend_id,
            "backend_version": backend_version,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ResourceUsage:
    resource: str
    used: int
    limit: int
    unit: str = "bytes"
    path: str = ""

    @property
    def remaining(self) -> int:
        return self.limit - self.used

    def diagnostic(self) -> Diagnostic | None:
        if self.used <= self.limit:
            return None
        return Diagnostic(
            "error",
            "budget.exceeded",
            f"{self.resource} budget exceeded: {self.used}/{self.limit} {self.unit}",
            self.path,
        )


def budget_diagnostics(usages: Iterable[ResourceUsage]) -> list[Diagnostic]:
    return [diagnostic for usage in usages if (diagnostic := usage.diagnostic()) is not None]


def hash_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def hash_file(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ContentCache:
    """Small deterministic content-addressed cache used by host tooling.

    Values are opaque bytes. The cache deliberately knows nothing about target
    file formats; backends decide what a converted payload means.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def _path(self, key: str) -> Path:
        if len(key) != 64 or any(ch not in "0123456789abcdef" for ch in key):
            raise ValueError("cache key must be a lowercase SHA-256 hex digest")
        return self.root / key[:2] / key[2:]

    def put(self, key: str, data: bytes) -> Path:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def get(self, key: str) -> bytes | None:
        path = self._path(key)
        return path.read_bytes() if path.is_file() else None

    def contains(self, key: str) -> bool:
        return self._path(key).is_file()
