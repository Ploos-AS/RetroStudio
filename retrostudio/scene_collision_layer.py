"""Tk-canvas compatible rendering and paint preview for collision authoring."""

from __future__ import annotations

from .collision_editor import overlays_for_entity, paint_box


class SceneCollisionLayer:
    """Render collision geometry and turn canvas drags into model edits."""

    TAG = "retrostudio-collision"
    PREVIEW_TAG = "retrostudio-collision-preview"

    def __init__(self, canvas, entity) -> None:
        self.canvas = canvas
        self.entity = entity
        self._paint_start = None

    def render(self) -> None:
        self.canvas.delete(self.TAG)
        for overlay in overlays_for_entity(self.entity):
            tags = (self.TAG, f"collision:{overlay.kind}")
            dash = (6, 3) if overlay.kind == "trigger" else ()
            if overlay.shape == "circle":
                r = overlay.radius
                self.canvas.create_oval(overlay.x - r, overlay.y - r, overlay.x + r, overlay.y + r, dash=dash, width=2, tags=tags)
            else:
                self.canvas.create_rectangle(overlay.x, overlay.y, overlay.x + overlay.width, overlay.y + overlay.height, dash=dash, width=2, tags=tags)
            self.canvas.create_text(overlay.x, overlay.y - 6, anchor="sw", text=f"{overlay.kind.title()}: {overlay.label}", tags=tags)

    def begin_paint(self, x: float, y: float) -> None:
        self._paint_start = (float(x), float(y))
        self.canvas.delete(self.PREVIEW_TAG)

    def update_paint(self, x: float, y: float) -> None:
        if self._paint_start is None:
            return
        start_x, start_y = self._paint_start
        self.canvas.delete(self.PREVIEW_TAG)
        self.canvas.create_rectangle(start_x, start_y, float(x), float(y), dash=(4, 3), width=2, tags=(self.PREVIEW_TAG,))

    def finish_paint(self, kind: str, x: float, y: float, *, label: str = "default", filter_tag: str = "", solid: bool = True) -> None:
        if self._paint_start is None:
            return
        start_x, start_y = self._paint_start
        self._paint_start = None
        self.canvas.delete(self.PREVIEW_TAG)
        paint_box(self.entity, kind, start_x, start_y, float(x), float(y), label=label, filter_tag=filter_tag, solid=solid)
