"""Platform-neutral RetroStudio project model used by host tools and tests."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

FORMAT_VERSION = 1


@dataclass(frozen=True)
class Diagnostic:
    level: str
    code: str
    message: str
    path: str = ""


@dataclass
class Component:
    type: str
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Component":
        return cls(type=str(raw["type"]), data=dict(raw.get("data", {})))

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "data": self.data}


@dataclass
class Entity:
    entity_id: str
    name: str
    components: list[Component] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Entity":
        return cls(
            entity_id=str(raw["entity_id"]),
            name=str(raw.get("name", raw["entity_id"])),
            components=[Component.from_dict(item) for item in raw.get("components", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "components": [component.to_dict() for component in self.components],
        }


@dataclass
class Scene:
    scene_id: str
    name: str
    entities: list[Entity] = field(default_factory=list)
    source_path: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any], source_path: str = "") -> "Scene":
        if raw.get("format_version") != FORMAT_VERSION:
            raise ValueError("unsupported scene format_version")
        return cls(
            scene_id=str(raw["scene_id"]),
            name=str(raw.get("name", raw["scene_id"])),
            entities=[Entity.from_dict(item) for item in raw.get("entities", [])],
            source_path=source_path,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_version": FORMAT_VERSION,
            "scene_id": self.scene_id,
            "name": self.name,
            "entities": [entity.to_dict() for entity in self.entities],
        }


@dataclass
class Project:
    name: str
    project_id: str
    default_scene: str
    scenes: list[Scene]
    assets: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    source_path: str = ""

    def diagnostics(self) -> list[Diagnostic]:
        out: list[Diagnostic] = []
        scene_paths = [scene.source_path for scene in self.scenes]
        if self.default_scene and self.default_scene not in scene_paths:
            out.append(Diagnostic("error", "project.default_scene_missing", "default_scene is not in project scenes", "default_scene"))

        ids: set[str] = set()
        for scene in self.scenes:
            if scene.scene_id in ids:
                out.append(Diagnostic("error", "scene.duplicate_id", f"duplicate scene id: {scene.scene_id}", scene.source_path))
            ids.add(scene.scene_id)
            entity_ids: set[str] = set()
            for entity in scene.entities:
                if entity.entity_id in entity_ids:
                    out.append(Diagnostic("error", "entity.duplicate_id", f"duplicate entity id: {entity.entity_id}", scene.source_path))
                entity_ids.add(entity.entity_id)
        return out


def _normalize_relpath(value: str) -> str:
    normalized = Path(value).as_posix()
    if normalized.startswith("/") or normalized == ".." or normalized.startswith("../"):
        raise ValueError(f"path must be project-relative: {value}")
    return normalized


def load_project(path: str | Path) -> Project:
    project_path = Path(path)
    raw = json.loads(project_path.read_text(encoding="utf-8"))
    if raw.get("format_version") != FORMAT_VERSION:
        raise ValueError("unsupported project format_version")

    root = project_path.parent
    scene_paths = [_normalize_relpath(str(item)) for item in raw.get("scenes", [])]
    scenes: list[Scene] = []
    for relpath in scene_paths:
        scene_raw = json.loads((root / relpath).read_text(encoding="utf-8"))
        scenes.append(Scene.from_dict(scene_raw, relpath))

    return Project(
        name=str(raw["name"]),
        project_id=str(raw["project_id"]),
        default_scene=_normalize_relpath(str(raw.get("default_scene", ""))) if raw.get("default_scene") else "",
        scenes=scenes,
        assets=[_normalize_relpath(str(item)) for item in raw.get("assets", [])],
        targets=[str(item) for item in raw.get("targets", [])],
        source_path=project_path.as_posix(),
    )


def save_project(project: Project, path: str | Path) -> None:
    project_path = Path(path)
    root = project_path.parent
    root.mkdir(parents=True, exist_ok=True)

    scene_paths: list[str] = []
    for index, scene in enumerate(project.scenes):
        relpath = scene.source_path or f"scenes/{scene.scene_id or index}.scene.json"
        relpath = _normalize_relpath(relpath)
        target = root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(scene.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        scene_paths.append(relpath)

    raw = {
        "format_version": FORMAT_VERSION,
        "name": project.name,
        "project_id": project.project_id,
        "default_scene": project.default_scene,
        "scenes": scene_paths,
        "assets": sorted(project.assets),
        "targets": sorted(project.targets),
    }
    project_path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
