"""Toolkit-neutral scene transform helpers for creator frontends."""

from __future__ import annotations

GRID_SIZES = (0, 8, 16, 32)


def snap(value: float, grid: int = 8) -> int:
    """Snap a scene coordinate, or round to pixels when snapping is disabled."""
    if grid < 0:
        raise ValueError("grid must not be negative")
    if grid == 0:
        return int(round(float(value)))
    return int(round(float(value) / grid) * grid)


def transform_component(entity):
    for component in entity.components:
        if component.type == "transform":
            return component
    return None


def move_entity(entity, x: float, y: float, *, grid: int = 8) -> tuple[int, int]:
    """Move an entity's existing transform to a scene position."""
    component = transform_component(entity)
    if component is None:
        raise ValueError(f"entity has no transform: {entity.entity_id}")
    position = snap(x, grid), snap(y, grid)
    component.data["x"], component.data["y"] = position
    return position


def nudge_entity(entity, dx: int, dy: int, *, grid: int = 8) -> tuple[int, int]:
    """Nudge an entity by one logical step while respecting current grid mode."""
    component = transform_component(entity)
    if component is None:
        raise ValueError(f"entity has no transform: {entity.entity_id}")
    step = grid if grid > 0 else 1
    x = float(component.data.get("x", 0)) + int(dx) * step
    y = float(component.data.get("y", 0)) + int(dy) * step
    return move_entity(entity, x, y, grid=grid)
