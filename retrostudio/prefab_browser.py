"""Toolkit-neutral prefab browser state for creator frontends."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .behaviours import FIELDS
from .model import Scene
from .prefab import PREFABS, PrefabDefinition, instantiate_prefab


@dataclass(frozen=True)
class PrefabField:
    component_type: str
    key: str
    label: str
    field_type: str
    value: Any
    choices: tuple[str, ...] = ()


class PrefabBrowser:
    """Expose grouped creator templates and configure them before placement."""

    def __init__(self, prefabs: tuple[PrefabDefinition, ...] = PREFABS) -> None:
        self.prefabs = tuple(prefabs)

    @property
    def genres(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(item.genre for item in self.prefabs))

    def items(self, genre: str | None = None) -> tuple[PrefabDefinition, ...]:
        if genre is None:
            return self.prefabs
        return tuple(item for item in self.prefabs if item.genre == genre)

    def definition(self, prefab_id: str) -> PrefabDefinition:
        for item in self.prefabs:
            if item.prefab_id == prefab_id:
                return item
        raise ValueError(f"prefab is not available in this browser: {prefab_id}")

    def fields(self, prefab_id: str) -> tuple[PrefabField, ...]:
        definition = self.definition(prefab_id)
        out: list[PrefabField] = []
        for component in definition.components:
            if not component.type.startswith("behaviour."):
                continue
            behaviour = component.type.split(".", 1)[1]
            for field in FIELDS.get(behaviour, ()):
                out.append(PrefabField(component.type, field.key, field.label, field.field_type, deepcopy(component.data.get(field.key)), field.choices))
        return tuple(out)

    def place(self, scene: Scene, prefab_id: str, *, x: int = 64, y: int = 64, name: str | None = None, values: dict[tuple[str, str], Any] | None = None):
        self.definition(prefab_id)
        entity = instantiate_prefab(scene, prefab_id, x=x, y=y)
        if name is not None and name.strip():
            entity.name = name.strip()
        for component in entity.components:
            for (component_type, key), value in (values or {}).items():
                if component.type == component_type:
                    component.data[key] = value
        return entity
