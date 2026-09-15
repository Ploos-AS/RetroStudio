"""Interactive collision overlay/painting layer for the native Scene Composer."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from .collision_editor import overlays_for_entity, paint_box
from .model import Entity


class SceneCollisionLayer:
    """Bind collision painting and overlays to an existing Tk Canvas.

    Project semantics stay in collision_editor; this class only translates mouse
    gestures and renders the resulting canonical geometry.
    """

    HANDLE_SIZE = 4

    def __init__(self, canvas: tk.Canvas, on_changed: Callable[[], None] | None = None) -> None:
        self.canvas = canvas
        self.on_changed = on_changed or (lambda: None)
        self.entity: Entity | None = None
        self.mode: str | None = None
        self.label = "default"
        self.filter_tag = ""
        self._start: tuple[float, float] | None = None
        self._preview: int | None = None
        canvas.bind("<ButtonPress-1>", self._press, add="+")
        canvas.bind("<B1-Motion>", self._motion, add="+")
        canvas.bind("<ButtonRelease-1>", self._release, add="+")

    def select(self, entity: Entity | None) -> None:
        self.entity = entity
        self.redraw()

    def arm(self, kind: str, label: str = "default", filter_tag: str = "") -> None:
        if kind not in ("collider", "trigger"):
            raise ValueError(f"unknown collision kind: {kind}")
        self.mode = kind
        self.label = label
        self.filter_tag = filter_tag

    def disarm(self) -> None:
        self.mode = None
        self._start = None
        self._delete_preview()

    def redraw(self) -> None:
        self.canvas.delete("collision-overlay")
        if self.entity is None:
            return
        for overlay in overlays_for_entity(self.entity):
            tags = ("collision-overlay", f"collision-{overlay.kind}")
            if overlay.shape == "circle":
                r = overlay.radius
                self.canvas.create_oval(overlay.x - r, overlay.y - r, overlay.x + r, overlay.y + r, dash=(4, 2), width=2, tags=tags)
                self._handle(overlay.x + r, overlay.y)
            else:
                self.canvas.create_rectangle(overlay.x, overlay.y, overlay.x + overlay.width, overlay.y + overlay.height, dash=(4, 2), width=2, tags=tags)
                self._handle(overlay.x, overlay.y)
                self._handle(overlay.x + overlay.width, overlay.y + overlay.height)
            self.canvas.create_text(overlay.x + 4, overlay.y - 4, anchor="sw", text=f"{overlay.kind}: {overlay.label}", tags=tags)

    def _handle(self, x: float, y: float) -> None:
        s = self.HANDLE_SIZE
        self.canvas.create_rectangle(x - s, y - s, x + s, y + s, tags=("collision-overlay", "collision-handle"))

    def _press(self, event) -> None:
        if self.mode is None or self.entity is None:
            return
        self._start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self._delete_preview()

    def _motion(self, event) -> None:
        if self._start is None:
            return
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        x0, y0 = self._start
        left, right = sorted((x0, x))
        top, bottom = sorted((y0, y))
        if self._preview is None:
            self._preview = self.canvas.create_rectangle(left, top, right, bottom, dash=(2, 2), width=2, tags=("collision-paint-preview",))
        else:
            self.canvas.coords(self._preview, left, top, right, bottom)

    def _release(self, event) -> None:
        if self._start is None or self.mode is None or self.entity is None:
            return
        end = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        start = self._start
        self._start = None
        self._delete_preview()
        try:
            paint_box(self.entity, self.mode, start[0], start[1], end[0], end[1], label=self.label, filter_tag=self.filter_tag)
        except ValueError:
            return
        self.redraw()
        self.on_changed()

    def _delete_preview(self) -> None:
        if self._preview is not None:
            self.canvas.delete(self._preview)
            self._preview = None
