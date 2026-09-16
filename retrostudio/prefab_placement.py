"""Toolkit-neutral state for placing creator templates in the Scene Composer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .prefab_browser import PrefabBrowser


@dataclass
class PrefabPlacementSession:
    """Hold a configured template until the creator chooses its scene position."""

    browser: PrefabBrowser
    prefab_id: str
    name: str | None = None
    values: dict[tuple[str, str], Any] | None = None
    active: bool = True

    @property
    def preview(self):
        return self.browser.preview(self.prefab_id)

    def bounds_at(self, x: float, y: float) -> tuple[float, float, float, float]:
        preview = self.preview
        return (
            float(x) - preview.width / 2,
            float(y) - preview.height / 2,
            float(x) + preview.width / 2,
            float(y) + preview.height / 2,
        )

    def place(self, scene, x: float, y: float):
        if not self.active:
            raise ValueError("placement session is no longer active")
        entity = self.browser.place(
            scene,
            self.prefab_id,
            x=round(float(x) - self.preview.width / 2),
            y=round(float(y) - self.preview.height / 2),
            name=self.name,
            values=self.values,
        )
        self.active = False
        return entity

    def cancel(self) -> None:
        self.active = False
