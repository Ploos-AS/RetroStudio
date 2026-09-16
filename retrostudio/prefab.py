"""Platform-neutral creator prefabs built from ordinary RetroStudio components."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .behaviours import BehaviourDefinition
from .collision import CollisionShape
from .model import Component, Entity, Scene


@dataclass(frozen=True)
class PrefabDefinition:
    prefab_id: str
    name: str
    genre: str
    components: tuple[Component, ...]
    description: str = ""

    def instantiate(self, entity_id: str, *, x: int = 0, y: int = 0) -> Entity:
        components = [Component("transform", {"x": int(x), "y": int(y)})]
        components.extend(Component(item.type, deepcopy(item.data)) for item in self.components)
        return Entity(str(entity_id), self.name, components)


def _behaviour(kind: str, **values) -> Component:
    return BehaviourDefinition(kind, values).to_component()


def _collider(width: float = 16, height: float = 16) -> Component:
    return Component(
        "collision.collider",
        {"shape": CollisionShape("box", width=width, height=height).to_dict(), "layer": "default", "solid": True},
    )


PREFABS: tuple[PrefabDefinition, ...] = (
    PrefabDefinition(
        "platformer.player",
        "Player",
        "platformer",
        (_behaviour("PlatformerPlayer"), _behaviour("CameraFollow"), _collider(16, 28)),
        "Playable platform character with movement, camera follow and collision.",
    ),
    PrefabDefinition(
        "platformer.enemy_patrol",
        "Patrol Enemy",
        "platformer",
        (_behaviour("EnemyPatrol"), _collider(16, 16)),
        "Simple enemy that patrols a configurable distance.",
    ),
    PrefabDefinition(
        "platformer.collectible",
        "Collectible",
        "platformer",
        (_behaviour("Collectible"),),
        "Score/item pickup ready for creator artwork.",
    ),
    PrefabDefinition(
        "adventure.door",
        "Door",
        "adventure",
        (_behaviour("Door"), _collider(16, 32)),
        "Interactive door with optional item/tag requirement.",
    ),
    PrefabDefinition(
        "adventure.dialogue_npc",
        "Dialogue NPC",
        "adventure",
        (_behaviour("Dialogue"), _collider(16, 24)),
        "NPC foundation with creator-editable dialogue.",
    ),
    PrefabDefinition(
        "action.projectile",
        "Projectile",
        "action",
        (_behaviour("Projectile"), _collider(8, 8)),
        "Small moving projectile foundation.",
    ),
)


def prefab(prefab_id: str) -> PrefabDefinition:
    for item in PREFABS:
        if item.prefab_id == prefab_id:
            return item
    raise ValueError(f"unknown prefab: {prefab_id}")


def prefabs_for_genre(genre: str) -> tuple[PrefabDefinition, ...]:
    return tuple(item for item in PREFABS if item.genre == genre)


def instantiate_prefab(scene: Scene, prefab_id: str, *, x: int = 0, y: int = 0, entity_id: str | None = None) -> Entity:
    definition = prefab(prefab_id)
    used = {entity.entity_id for entity in scene.entities}
    base = entity_id or prefab_id.replace(".", "-").replace("_", "-")
    candidate = base
    index = 2
    while candidate in used:
        candidate = f"{base}-{index}"
        index += 1
    entity = definition.instantiate(candidate, x=x, y=y)
    scene.entities.append(entity)
    return entity
