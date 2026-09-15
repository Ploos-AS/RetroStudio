"""Toolkit-neutral collision editing helpers for creator frontends."""

from __future__ import annotations

from dataclasses import dataclass

from .collision import COLLIDER_COMPONENT, TRIGGER_COMPONENT, CollisionShape, set_collider, set_trigger
from .model import Entity


@dataclass(frozen=True)
class CollisionOverlay:
    kind: str
    shape: str
    x: float
    y: float
    width: float = 0.0
    height: float = 0.0
    radius: float = 0.0
    label: str = ""


def _position(entity: Entity) -> tuple[float, float]:
    for component in entity.components:
        if component.type == "transform":
            return float(component.data.get("x", 0)), float(component.data.get("y", 0))
    return 0.0, 0.0


def _component(entity: Entity, component_type: str):
    for component in entity.components:
        if component.type == component_type:
            return component
    return None


def overlays_for_entity(entity: Entity) -> list[CollisionOverlay]:
    """Return scene-space overlays without depending on a GUI toolkit."""
    base_x, base_y = _position(entity)
    overlays: list[CollisionOverlay] = []
    for kind, component_type in (("collider", COLLIDER_COMPONENT), ("trigger", TRIGGER_COMPONENT)):
        component = _component(entity, component_type)
        if component is None:
            continue
        shape_data = component.data.get("shape", {})
        if not isinstance(shape_data, dict):
            continue
        shape = CollisionShape.from_dict(shape_data)
        label = str(component.data.get("layer", "default")) if kind == "collider" else str(component.data.get("event", "trigger"))
        overlays.append(
            CollisionOverlay(
                kind=kind,
                shape=shape.shape,
                x=base_x + shape.x,
                y=base_y + shape.y,
                width=shape.width,
                height=shape.height,
                radius=shape.radius,
                label=label,
            )
        )
    return overlays


def apply_box_collider(entity: Entity, x: float, y: float, width: float, height: float, layer: str = "default", solid: bool = True) -> None:
    shape = CollisionShape("box", float(x), float(y), float(width), float(height))
    if shape.diagnostics():
        raise ValueError("collider width and height must be greater than zero")
    set_collider(entity, shape, layer=layer.strip() or "default", solid=solid)


def apply_circle_collider(entity: Entity, x: float, y: float, radius: float, layer: str = "default", solid: bool = True) -> None:
    shape = CollisionShape("circle", float(x), float(y), radius=float(radius))
    if shape.diagnostics():
        raise ValueError("collider radius must be greater than zero")
    set_collider(entity, shape, layer=layer.strip() or "default", solid=solid)


def apply_box_trigger(entity: Entity, x: float, y: float, width: float, height: float, event: str, filter_tag: str = "") -> None:
    if not event.strip():
        raise ValueError("trigger event is required")
    shape = CollisionShape("box", float(x), float(y), float(width), float(height))
    if shape.diagnostics():
        raise ValueError("trigger width and height must be greater than zero")
    set_trigger(entity, shape, event.strip(), filter_tag.strip())


def remove_collision(entity: Entity, kind: str) -> None:
    component_type = COLLIDER_COMPONENT if kind == "collider" else TRIGGER_COMPONENT if kind == "trigger" else ""
    if not component_type:
        raise ValueError(f"unknown collision kind: {kind}")
    entity.components[:] = [component for component in entity.components if component.type != component_type]
