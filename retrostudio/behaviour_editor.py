"""Toolkit-neutral creator-facing behaviour editor helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .behaviours import (
    BEHAVIOUR_TYPES,
    BehaviourDefinition,
    BehaviourField,
    add_behaviour,
    behaviour_fields,
    entity_behaviours,
    remove_behaviour,
    update_behaviour,
)
from .model import Entity


@dataclass(frozen=True)
class BehaviourEditorState:
    available: tuple[str, ...]
    attached: tuple[BehaviourDefinition, ...]


def editor_state(entity: Entity) -> BehaviourEditorState:
    return BehaviourEditorState(BEHAVIOUR_TYPES, tuple(entity_behaviours(entity)))


def editor_fields(behaviour: str) -> tuple[BehaviourField, ...]:
    return behaviour_fields(behaviour)


def parse_editor_values(behaviour: str, raw: dict[str, Any]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for field in behaviour_fields(behaviour):
        value = raw.get(field.key)
        if field.field_type == "number":
            if isinstance(value, (int, float)):
                parsed[field.key] = value
            else:
                text = str(value).strip()
                parsed[field.key] = float(text) if "." in text else int(text)
        elif field.field_type == "boolean":
            if isinstance(value, bool):
                parsed[field.key] = value
            else:
                parsed[field.key] = str(value).strip().lower() in ("1", "true", "yes", "on")
        else:
            parsed[field.key] = "" if value is None else str(value)
    return parsed


def add_from_editor(entity: Entity, behaviour: str, raw: dict[str, Any] | None = None) -> None:
    values = parse_editor_values(behaviour, raw or {}) if raw else {}
    add_behaviour(entity, BehaviourDefinition(behaviour, values))


def update_from_editor(entity: Entity, behaviour: str, raw: dict[str, Any]) -> None:
    values = parse_editor_values(behaviour, raw)
    update_behaviour(entity, BehaviourDefinition(behaviour, values))


def remove_from_editor(entity: Entity, behaviour: str) -> bool:
    return remove_behaviour(entity, behaviour)
