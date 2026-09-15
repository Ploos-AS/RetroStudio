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
        overlays.append(CollisionOverlay(kind, shape.shape, base_x + shape.x, base_y + shape.y, shape.width, shape.height, shape.radius, label))
    return overlays


def box_from_drag(entity: Entity, start_x: float, start_y: float, end_x: float, end_y: float) -> CollisionShape:
    """Convert a scene-canvas drag into entity-local normalized box geometry."""
    base_x, base_y = _position(entity)
    left, right = sorted((float(start_x), float(end_x)))
    top, bottom = sorted((float(start_y), float(end_y)))
    return CollisionShape("box", left - base_x, top - base_y, right - left, bottom - top)


def resize_box_from_scene(entity: Entity, x: float, y: float, width: float, height: float) -> CollisionShape:
    """Convert scene-space box bounds, as produced by resize handles, to local geometry."""
    base_x, base_y = _position(entity)
    return CollisionShape("box", float(x) - base_x, float(y) - base_y, float(width), float(height))


def resize_box(entity: Entity, kind: str, x: float, y: float, width: float, height: float) -> None:
    """Resize an existing box collision component while preserving its metadata."""
    component_type = COLLIDER_COMPONENT if kind == "collider" else TRIGGER_COMPONENT if kind == "trigger" else ""
    if not component_type:
        raise ValueError(f"unknown collision kind: {kind}")
    component = _component(entity, component_type)
    if component is None:
        raise ValueError(f"entity has no {kind}")
    shape = resize_box_from_scene(entity, x, y, width, height)
    if shape.diagnostics():
        raise ValueError("resized collision area must have positive width and height")
    if kind == "collider":
        set_collider(entity, shape, layer=str(component.data.get("layer", "default")), solid=bool(component.data.get("solid", True)))
    else:
        event = str(component.data.get("event", "")).strip()
        if not event:
            raise ValueError("trigger event is required")
        set_trigger(entity, shape, event, str(component.data.get("filter_tag", "")))


def resize_circle(entity: Entity, kind: str, center_x: float, center_y: float, radius: float) -> None:
    """Resize an existing circle collision component while preserving metadata."""
    component_type = COLLIDER_COMPONENT if kind == "collider" else TRIGGER_COMPONENT if kind == "trigger" else ""
    if not component_type:
        raise ValueError(f"unknown collision kind: {kind}")
    component = _component(entity, component_type)
    if component is None:
        raise ValueError(f"entity has no {kind}")
    base_x, base_y = _position(entity)
    shape = CollisionShape("circle", float(center_x) - base_x, float(center_y) - base_y, radius=float(radius))
    if shape.diagnostics():
        raise ValueError("resized collision radius must be greater than zero")
    if kind == "collider":
        set_collider(entity, shape, layer=str(component.data.get("layer", "default")), solid=bool(component.data.get("solid", True)))
    else:
        event = str(component.data.get("event", "")).strip()
        if not event:
            raise ValueError("trigger event is required")
        set_trigger(entity, shape, event, str(component.data.get("filter_tag", "")))


def paint_box(entity: Entity, kind: str, start_x: float, start_y: float, end_x: float, end_y: float, *, label: str = "default", filter_tag: str = "", solid: bool = True) -> None:
    """Apply a box painted directly on a scene canvas."""
    shape = box_from_drag(entity, start_x, start_y, end_x, end_y)
    if shape.diagnostics():
        raise ValueError("painted collision area must have positive width and height")
    if kind == "collider":
        set_collider(entity, shape, layer=label.strip() or "default", solid=solid)
    elif kind == "trigger":
        if not label.strip():
            raise ValueError("trigger event is required")
        set_trigger(entity, shape, label.strip(), filter_tag.strip())
    else:
        raise ValueError(f"unknown collision kind: {kind}")


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
