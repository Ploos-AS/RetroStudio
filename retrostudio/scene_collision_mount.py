"""Mount collision authoring controls onto a Scene Composer canvas.

This adapter keeps CreatorShell wiring small: the desktop owns selection and
persistence while the collision modules own pointer gestures and widgets.
"""

from __future__ import annotations

from .collision_toolbar import CollisionToolbar
from .desktop_collision import CollisionToolState, SceneCollisionController


class SceneCollisionMount:
    """Own the toolbar/controller pair for one selected scene entity."""

    def __init__(self, toolbar_parent, canvas, entity, *, state=None, on_change=None, on_status=None) -> None:
        self.state = state or CollisionToolState()
        self.on_status = on_status
        self.toolbar = CollisionToolbar(toolbar_parent, self.state, on_tool_change=self._tool_changed)
        self.controller = SceneCollisionController(canvas, entity, self.state, on_change=on_change)

    def mount(self) -> None:
        self.toolbar.pack(fill="x", pady=(0, 6))
        self.controller.bind()
        self.canvas = self.controller.canvas
        self.canvas.bind("<ButtonPress-1>", self._before_pointer_down, add="+")
        self.controller.render()
        self._tool_changed(self.state)

    def _before_pointer_down(self, _event) -> None:
        self.sync_before_gesture()

    def _tool_changed(self, state: CollisionToolState) -> None:
        if self.on_status is None:
            return
        if state.tool == "select":
            self.on_status("Collision tool: Select")
        elif state.tool == "collider":
            self.on_status(f"Collision tool: Collider — layer {state.collider_layer}")
        else:
            self.on_status(f"Collision tool: Trigger — event {state.trigger_event}")

    def sync_before_gesture(self) -> None:
        """Copy editable toolbar values into shared state before painting."""
        self.toolbar.sync()
