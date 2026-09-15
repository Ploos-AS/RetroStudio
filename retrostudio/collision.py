"""Platform-neutral collision shapes and trigger authoring for RetroStudio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import Component, Diagnostic, Entity

COLLIDER_COMPONENT = "collision.collider"
TRIGGER_COMPONENT = "collision.trigger"
SHAPE_TYPES = ("box", "circle")


@dataclass(frozen=True)
class CollisionShape:
    shape: str = "box"
    x: float = 0.0
    y: float = 0.0
    width: float = 16.0
    height: float = 16.0
    radius: float = 8.0

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CollisionShape":
        return cls(
            shape=str(raw.get("shape", "box")),
            x=float(raw.get("x", 0.0)),
            y=float(raw.get("y", 0.0)),
            width=float(raw.get("width", 16.0)),
            height=float(raw.get("height", 16.0)),
            radius=float(raw.get("radius", 8.0)),
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"shape": self.shape, "x": self.x, "y": self.y}
        if self.shape == "circle":
            out["radius"] = self.radius
        else:
            out["width"] = self.width
            out["height"] = self.height
        return out

    def diagnostics(self, path: str = "") -> list[Diagnostic]:
        out: list[Diagnostic] = []
        if self.shape not in SHAPE_TYPES:
            out.append(Diagnostic("error", "collision.shape_unknown", f"unknown collision shape: {self.shape}", path))
        elif self.shape == "box" and (self.width <= 0 or self.height <= 0):
            out.append(Diagnostic("error", "collision.box_size", "box width and height must be positive", path))
        elif self.shape == "circle" and self.radius <= 0:
            out.append(Diagnostic("error", "collision.circle_radius", "circle radius must be positive", path))
        return out


def _component(entity: Entity, component_type: str) -> Component | None:
    return next((item for item in entity.components if item.type == component_type), None)


def set_collider(entity: Entity, shape: CollisionShape, *, layer: str = "default", solid: bool = True) -> Component:
    data = {"shape": shape.to_dict(), "layer": layer, "solid": bool(solid)}
    component = _component(entity, COLLIDER_COMPONENT)
    if component is None:
        component = Component(COLLIDER_COMPONENT, data)
        entity.components.append(component)
    else:
        component.data = data
    return component


def set_trigger(entity: Entity, shape: CollisionShape, *, event: str, filter_tag: str = "") -> Component:
    data = {"shape": shape.to_dict(), "event": event, "filter_tag": filter_tag}
    component = _component(entity, TRIGGER_COMPONENT)
    if component is None:
        component = Component(TRIGGER_COMPONENT, data)
        entity.components.append(component)
    else:
        component.data = data
    return component


def collision_diagnostics(entity: Entity) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    for component in entity.components:
        if component.type not in (COLLIDER_COMPONENT, TRIGGER_COMPONENT):
            continue
        path = f"entity:{entity.entity_id}/{component.type}"
        raw_shape = component.data.get("shape")
        if not isinstance(raw_shape, dict):
            out.append(Diagnostic("error", "collision.shape_missing", "collision component requires a shape", path))
            continue
        out.extend(CollisionShape.from_dict(raw_shape).diagnostics(path))
        if component.type == TRIGGER_COMPONENT and not str(component.data.get("event", "")).strip():
            out.append(Diagnostic("error", "collision.trigger_event", "trigger requires an event name", path))
    return out
