"""Interactive collision overlay/painting layer for the native Scene Composer."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from .collision_editor import overlays_for_entity, paint_box, resize_box
from .model import Entity


class SceneCollisionLayer:
    """Bind collision painting, box resizing and overlays to an existing Tk Canvas."""

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
        self._resize: tuple[str, str, float, float, float, float] | None = None
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
        self._resize = None
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
            else:
                self.canvas.create_rectangle(overlay.x, overlay.y, overlay.x + overlay.width, overlay.y + overlay.height, dash=(4, 2), width=2, tags=tags)
                self._handle(overlay.kind, "nw", overlay.x, overlay.y)
                self._handle(overlay.kind, "se", overlay.x + overlay.width, overlay.y + overlay.height)
            self.canvas.create_text(overlay.x + 4, overlay.y - 4, anchor="sw", text=f"{overlay.kind}: {overlay.label}", tags=tags)

    def _handle(self, kind: str, corner: str, x: float, y: float) -> None:
        s = self.HANDLE_SIZE
        self.canvas.create_rectangle(
            x - s, y - s, x + s, y + s,
            tags=("collision-overlay", "collision-handle", f"collision-handle:{kind}:{corner}"),
        )

    def _scene_point(self, event) -> tuple[float, float]:
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

    def _handle_at(self, event) -> tuple[str, str] | None:
        current = self.canvas.find_withtag("current")
        if not current:
            return None
        for tag in self.canvas.gettags(current[0]):
            if tag.startswith("collision-handle:"):
                _, kind, corner = tag.split(":", 2)
                return kind, corner
        return None

    def _overlay(self, kind: str):
        if self.entity is None:
            return None
        return next((overlay for overlay in overlays_for_entity(self.entity) if overlay.kind == kind and overlay.shape == "box"), None)

    def _press(self, event) -> None:
        if self.entity is None:
            return
        handle = self._handle_at(event)
        if handle is not None:
            kind, corner = handle
            overlay = self._overlay(kind)
            if overlay is not None:
                self._resize = (kind, corner, overlay.x, overlay.y, overlay.x + overlay.width, overlay.y + overlay.height)
                self._delete_preview()
                return
        if self.mode is None:
            return
        self._start = self._scene_point(event)
        self._delete_preview()

    def _resize_bounds(self, point: tuple[float, float]) -> tuple[float, float, float, float] | None:
        if self._resize is None:
            return None
        _kind, corner, left, top, right, bottom = self._resize
        x, y = point
        if corner == "nw":
            left, top = x, y
        else:
            right, bottom = x, y
        left, right = sorted((left, right))
        top, bottom = sorted((top, bottom))
        return left, top, right, bottom

    def _show_preview(self, left: float, top: float, right: float, bottom: float) -> None:
        if self._preview is None:
            self._preview = self.canvas.create_rectangle(left, top, right, bottom, dash=(2, 2), width=2, tags=("collision-paint-preview",))
        else:
            self.canvas.coords(self._preview, left, top, right, bottom)

    def _motion(self, event) -> None:
        point = self._scene_point(event)
        bounds = self._resize_bounds(point)
        if bounds is not None:
            self._show_preview(*bounds)
            return
        if self._start is None:
            return
        x, y = point
        x0, y0 = self._start
        left, right = sorted((x0, x))
        top, bottom = sorted((y0, y))
        self._show_preview(left, top, right, bottom)

    def _release(self, event) -> None:
        if self.entity is None:
            return
        if self._resize is not None:
            kind = self._resize[0]
            bounds = self._resize_bounds(self._scene_point(event))
            self._resize = None
            self._delete_preview()
            if bounds is None:
                return
            left, top, right, bottom = bounds
            try:
                resize_box(self.entity, kind, left, top, right - left, bottom - top)
            except ValueError:
                return
            self.redraw()
            self.on_changed()
            return
        if self._start is None or self.mode is None:
            return
        end = self._scene_point(event)
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
