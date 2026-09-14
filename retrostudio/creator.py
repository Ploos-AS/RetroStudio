"""Creator-facing asset and scene operations.

These functions keep source assets non-destructive: importing copies a source into
the project and scene placement only adds references/components.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .model import Component, Entity, Project, Scene


@dataclass(frozen=True)
class ImportedAsset:
    source: str
    project_path: str


def project_root(project: Project) -> Path:
    if not project.source_path:
        raise ValueError("project must be loaded/saved before importing assets")
    return Path(project.source_path).parent


def import_asset(project: Project, source: str | Path, asset_dir: str = "assets") -> ImportedAsset:
    src = Path(source)
    if not src.is_file():
        raise ValueError(f"asset source does not exist: {src}")
    root = project_root(project)
    destination_dir = root / asset_dir
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / src.name
    if destination.exists() and destination.read_bytes() != src.read_bytes():
        stem, suffix = src.stem, src.suffix
        index = 2
        while destination.exists():
            destination = destination_dir / f"{stem}-{index}{suffix}"
            index += 1
    if not destination.exists():
        shutil.copy2(src, destination)
    relpath = destination.relative_to(root).as_posix()
    if relpath not in project.assets:
        project.assets.append(relpath)
    return ImportedAsset(src.as_posix(), relpath)


def scene_by_id(project: Project, scene_id: str) -> Scene:
    for scene in project.scenes:
        if scene.scene_id == scene_id:
            return scene
    raise ValueError(f"unknown scene: {scene_id}")


def entity_by_id(scene: Scene, entity_id: str) -> Entity:
    for entity in scene.entities:
        if entity.entity_id == entity_id:
            return entity
    raise ValueError(f"unknown entity: {entity_id}")


def component_by_type(entity: Entity, component_type: str) -> Component | None:
    for component in entity.components:
        if component.type == component_type:
            return component
    return None


def place_asset(
    scene: Scene,
    asset_path: str,
    x: int = 0,
    y: int = 0,
    entity_id: str | None = None,
) -> Entity:
    base = Path(asset_path).stem.replace(" ", "-").lower() or "asset"
    used = {entity.entity_id for entity in scene.entities}
    candidate = entity_id or base
    index = 2
    while candidate in used:
        candidate = f"{base}-{index}"
        index += 1
    entity = Entity(
        entity_id=candidate,
        name=Path(asset_path).stem or candidate,
        components=[
            Component("transform", {"x": int(x), "y": int(y)}),
            Component("visual.asset", {"path": asset_path}),
        ],
    )
    scene.entities.append(entity)
    return entity


def rename_entity(entity: Entity, name: str) -> None:
    clean = str(name).strip()
    if not clean:
        raise ValueError("entity name must not be empty")
    entity.name = clean


def move_entity(entity: Entity, x: int, y: int) -> None:
    transform = component_by_type(entity, "transform")
    if transform is None:
        transform = Component("transform", {})
        entity.components.insert(0, transform)
    transform.data["x"] = int(x)
    transform.data["y"] = int(y)


def edit_entity(entity: Entity, *, name: str, x: int, y: int) -> None:
    """Apply the baseline creator-facing inspector fields atomically."""
    clean = str(name).strip()
    if not clean:
        raise ValueError("entity name must not be empty")
    parsed_x = int(x)
    parsed_y = int(y)
    rename_entity(entity, clean)
    move_entity(entity, parsed_x, parsed_y)
