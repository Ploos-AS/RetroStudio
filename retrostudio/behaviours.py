"""Creator-first reusable visual behaviours for RetroStudio.

Behaviours are platform-neutral authoring metadata. Target backends translate them
into runtime-specific implementations later; RetroStudio only owns the stable,
creator-facing schema and validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .model import Component, Diagnostic, Entity


BEHAVIOUR_TYPES = (
    "PlatformerPlayer",
    "CameraFollow",
    "EnemyPatrol",
    "Collectible",
    "Door",
    "Projectile",
)


DEFAULTS: dict[str, dict[str, Any]] = {
    "PlatformerPlayer": {"speed": 120, "jump_speed": 260, "gravity": 700},
    "CameraFollow": {"deadzone_x": 24, "deadzone_y": 16},
    "EnemyPatrol": {"speed": 48, "distance": 96, "axis": "x"},
    "Collectible": {"score": 1, "consume": True},
    "Door": {"starts_open": False, "requires": ""},
    "Projectile": {"speed": 220, "lifetime_ms": 1500, "direction": "facing"},
}


@dataclass(frozen=True)
class BehaviourDefinition:
    behaviour_type: str
    values: dict[str, Any] = field(default_factory=dict)

    def normalized_values(self) -> dict[str, Any]:
        if self.behaviour_type not in DEFAULTS:
            raise ValueError(f"unknown behaviour: {self.behaviour_type}")
        merged = dict(DEFAULTS[self.behaviour_type])
        merged.update(self.values)
        return merged

    def validate(self) -> list[Diagnostic]:
        if self.behaviour_type not in DEFAULTS:
            return [Diagnostic("error", "behaviour.unknown", f"unknown behaviour: {self.behaviour_type}")]
        values = self.normalized_values()
        out: list[Diagnostic] = []
        for key in ("speed", "jump_speed", "gravity", "distance", "score", "lifetime_ms"):
            if key in values and not isinstance(values[key], (int, float)):
                out.append(Diagnostic("error", "behaviour.value_type", f"{key} must be numeric", key))
        if "speed" in values and values["speed"] < 0:
            out.append(Diagnostic("error", "behaviour.speed_negative", "speed must not be negative", "speed"))
        if self.behaviour_type == "EnemyPatrol" and values["axis"] not in ("x", "y"):
            out.append(Diagnostic("error", "behaviour.axis_invalid", "patrol axis must be x or y", "axis"))
        if self.behaviour_type == "Projectile" and values["lifetime_ms"] <= 0:
            out.append(Diagnostic("error", "behaviour.lifetime_invalid", "projectile lifetime must be greater than zero", "lifetime_ms"))
        return out

    def to_component(self) -> Component:
        diagnostics = self.validate()
        if diagnostics:
            raise ValueError(diagnostics[0].message)
        return Component(f"behaviour.{self.behaviour_type}", self.normalized_values())


def behaviour_type(component: Component) -> str | None:
    prefix = "behaviour."
    return component.type[len(prefix):] if component.type.startswith(prefix) else None


def entity_behaviours(entity: Entity) -> list[BehaviourDefinition]:
    out: list[BehaviourDefinition] = []
    for component in entity.components:
        kind = behaviour_type(component)
        if kind is not None:
            out.append(BehaviourDefinition(kind, dict(component.data)))
    return out


def add_behaviour(entity: Entity, definition: BehaviourDefinition) -> Component:
    if any(behaviour_type(component) == definition.behaviour_type for component in entity.components):
        raise ValueError(f"entity already has behaviour: {definition.behaviour_type}")
    component = definition.to_component()
    entity.components.append(component)
    return component


def remove_behaviour(entity: Entity, behaviour: str) -> bool:
    for index, component in enumerate(entity.components):
        if behaviour_type(component) == behaviour:
            del entity.components[index]
            return True
    return False
