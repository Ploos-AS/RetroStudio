"""Tk-canvas compatible rendering and direct manipulation for collision authoring."""

from __future__ import annotations

from .collision_editor import overlays_for_entity, paint_box, resize_box


class SceneCollisionLayer:
    """Render collision geometry and turn canvas gestures into model edits."""

    TAG = "retrostudio-collision"
    PREVIEW_TAG = "retrostudio-collision-preview"
    HANDLE_TAG = "retrostudio-collision-handle"
    HANDLE_SIZE = 5

    def __init__(self, canvas, entity) -> None:
        self.canvas = canvas
        self.entity = entity
        self._paint_start = None
        self._resize = None

    def render(self) -> None:
        self.canvas.delete(self.TAG)
        for overlay in overlays_for_entity(self.entity):
            tags = (self.TAG, f"collision:{overlay.kind}")
            dash = (6, 3) if overlay.kind == "trigger" else ()
            if overlay.shape == "circle":
                r = overlay.radius
                self.canvas.create_oval(overlay.x - r, overlay.y - r, overlay.x + r, overlay.y + r, dash=dash, width=2, tags=tags)
            else:
                left, top = overlay.x, overlay.y
                right, bottom = left + overlay.width, top + overlay.height
                self.canvas.create_rectangle(left, top, right, bottom, dash=dash, width=2, tags=tags)
                self._handle(left, top, overlay.kind, "nw")
                self._handle(right, bottom, overlay.kind, "se")
            self.canvas.create_text(overlay.x, overlay.y - 6, anchor="sw", text=f"{overlay.kind.title()}: {overlay.label}", tags=tags)

    def _handle(self, x: float, y: float, kind: str, corner: str) -> None:
        size = self.HANDLE_SIZE
        self.canvas.create_rectangle(
            x - size,
            y - size,
            x + size,
            y + size,
            width=1,
            tags=(self.TAG, self.HANDLE_TAG, f"collision-handle:{kind}:{corner}"),
        )

    def handle_at(self, x: float, y: float):
        """Return (kind, corner) for a box resize handle at the scene point."""
        point_x, point_y = float(x), float(y)
        size = self.HANDLE_SIZE
        for overlay in overlays_for_entity(self.entity):
            if overlay.shape != "box":
                continue
            corners = (("nw", overlay.x, overlay.y), ("se", overlay.x + overlay.width, overlay.y + overlay.height))
            for corner, handle_x, handle_y in corners:
                if abs(point_x - handle_x) <= size and abs(point_y - handle_y) <= size:
                    return overlay.kind, corner
        return None

    def begin_resize(self, kind: str, corner: str) -> None:
        for overlay in overlays_for_entity(self.entity):
            if overlay.kind == kind and overlay.shape == "box":
                self._resize = (kind, corner, overlay.x, overlay.y, overlay.x + overlay.width, overlay.y + overlay.height)
                self.canvas.delete(self.PREVIEW_TAG)
                return

    def update_resize(self, x: float, y: float) -> None:
        bounds = self._resize_bounds(float(x), float(y))
        if bounds is None:
            return
        left, top, right, bottom = bounds
        self.canvas.delete(self.PREVIEW_TAG)
        self.canvas.create_rectangle(left, top, right, bottom, dash=(4, 3), width=2, tags=(self.PREVIEW_TAG,))

    def finish_resize(self, x: float, y: float) -> bool:
        bounds = self._resize_bounds(float(x), float(y))
        if bounds is None or self._resize is None:
            return False
        kind = self._resize[0]
        self._resize = None
        self.canvas.delete(self.PREVIEW_TAG)
        left, top, right, bottom = bounds
        if right <= left or bottom <= top:
            return False
        resize_box(self.entity, kind, left, top, right - left, bottom - top)
        return True

    def _resize_bounds(self, x: float, y: float):
        if self._resize is None:
            return None
        _kind, corner, left, top, right, bottom = self._resize
        if corner == "nw":
            left, top = x, y
        elif corner == "se":
            right, bottom = x, y
        else:
            return None
        return min(left, right), min(top, bottom), max(left, right), max(top, bottom)

    def begin_paint(self, x: float, y: float) -> None:
        self._paint_start = (float(x), float(y))
        self.canvas.delete(self.PREVIEW_TAG)

    def update_paint(self, x: float, y: float) -> None:
        if self._paint_start is None:
            return
        start_x, start_y = self._paint_start
        self.canvas.delete(self.PREVIEW_TAG)
        self.canvas.create_rectangle(start_x, start_y, float(x), float(y), dash=(4, 3), width=2, tags=(self.PREVIEW_TAG,))

    def finish_paint(self, kind: str, x: float, y: float, *, label: str = "default", filter_tag: str = "", solid: bool = True) -> bool:
        if self._paint_start is None:
            return False
        start_x, start_y = self._paint_start
        self._paint_start = None
        self.canvas.delete(self.PREVIEW_TAG)
        try:
            paint_box(self.entity, kind, start_x, start_y, float(x), float(y), label=label, filter_tag=filter_tag, solid=solid)
        except ValueError:
            return False
        return True
