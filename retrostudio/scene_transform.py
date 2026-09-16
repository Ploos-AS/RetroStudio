"""Toolkit-neutral scene transform helpers for creator frontends."""

from __future__ import annotations


def snap(value: float, grid: int = 8) -> int:
    """Snap a scene coordinate to the nearest positive grid interval."""
    if grid <= 0:
        raise ValueError("grid must be greater than zero")
    return int(round(float(value) / grid) * grid)


def transform_component(entity):
    for component in entity.components:
        if component.type == "transform":
            return component
    return None


def move_entity(entity, x: float, y: float, *, grid: int = 8) -> tuple[int, int]:
    """Move an entity's existing transform to a snapped scene position."""
    component = transform_component(entity)
    if component is None:
        raise ValueError(f"entity has no transform: {entity.entity_id}")
    position = snap(x, grid), snap(y, grid)
    component.data["x"], component.data["y"] = position
    return position
