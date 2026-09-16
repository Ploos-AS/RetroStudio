"""Toolkit-neutral prefab browser state for creator frontends."""

from __future__ import annotations

from .model import Scene
from .prefab import PREFABS, PrefabDefinition, instantiate_prefab


class PrefabBrowser:
    """Expose grouped creator templates and place them into scenes."""

    def __init__(self, prefabs: tuple[PrefabDefinition, ...] = PREFABS) -> None:
        self.prefabs = tuple(prefabs)

    @property
    def genres(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(item.genre for item in self.prefabs))

    def items(self, genre: str | None = None) -> tuple[PrefabDefinition, ...]:
        if genre is None:
            return self.prefabs
        return tuple(item for item in self.prefabs if item.genre == genre)

    def place(self, scene: Scene, prefab_id: str, *, x: int = 64, y: int = 64):
        if not any(item.prefab_id == prefab_id for item in self.prefabs):
            raise ValueError(f"prefab is not available in this browser: {prefab_id}")
        return instantiate_prefab(scene, prefab_id, x=x, y=y)
