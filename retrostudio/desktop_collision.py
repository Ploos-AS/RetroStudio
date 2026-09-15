"""Scene Composer collision-tool controller for the native desktop shell."""

from __future__ import annotations

from dataclasses import dataclass

from .scene_collision_layer import SceneCollisionLayer
from .model import Entity


@dataclass
class CollisionToolState:
    tool: str = "select"
    trigger_event: str = "trigger.enter"
    trigger_filter: str = ""
    collider_layer: str = "default"

    def choose(self, tool: str) -> None:
        if tool not in ("select", "collider", "trigger"):
            raise ValueError(f"unknown collision tool: {tool}")
        self.tool = tool

    @property
    def painting(self) -> bool:
        return self.tool in ("collider", "trigger")


class SceneCollisionController:
    """Translate Scene Composer pointer gestures into collision-layer operations."""

    def __init__(self, canvas, entity: Entity, state: CollisionToolState | None = None, on_change=None) -> None:
        self.canvas = canvas
        self.entity = entity
        self.state = state or CollisionToolState()
        self.on_change = on_change
        self.layer = SceneCollisionLayer(canvas, entity)
        self._dragging = False
        self._resizing = False

    def render(self) -> None:
        self.layer.render()

    def pointer_down(self, event) -> None:
        handle = self.layer.handle_at(float(event.x), float(event.y))
        if handle is not None:
            kind, corner = handle
            self._resizing = True
            self.layer.begin_resize(kind, corner)
            return
        if not self.state.painting:
            return
        self._dragging = True
        self.layer.begin_paint(float(event.x), float(event.y))

    def pointer_move(self, event) -> None:
        if self._resizing:
            self.layer.update_resize(float(event.x), float(event.y))
        elif self._dragging:
            self.layer.update_paint(float(event.x), float(event.y))

    def pointer_up(self, event) -> None:
        changed = False
        if self._resizing:
            self._resizing = False
            changed = self.layer.finish_resize(float(event.x), float(event.y))
        elif self._dragging:
            self._dragging = False
            label = self.state.collider_layer if self.state.tool == "collider" else self.state.trigger_event
            changed = self.layer.finish_paint(self.state.tool, float(event.x), float(event.y), label=label, filter_tag=self.state.trigger_filter)
        else:
            return
        self.layer.render()
        if changed and self.on_change is not None:
            self.on_change()

    def bind(self) -> None:
        self.canvas.bind("<ButtonPress-1>", self.pointer_down, add="+")
        self.canvas.bind("<B1-Motion>", self.pointer_move, add="+")
        self.canvas.bind("<ButtonRelease-1>", self.pointer_up, add="+")
