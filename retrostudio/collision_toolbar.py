"""Creator-facing Scene Composer collision toolbar.

The toolbar owns only Tk widgets and updates the platform-neutral collision tool
state. Pointer semantics remain in desktop_collision.py.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .desktop_collision import CollisionToolState


class CollisionToolbar(ttk.Frame):
    """Select/collider/trigger controls for the native Scene Composer."""

    def __init__(self, master, state: CollisionToolState, on_tool_change=None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.state = state
        self.on_tool_change = on_tool_change
        self.tool = tk.StringVar(value=state.tool)
        self.collider_layer = tk.StringVar(value=state.collider_layer)
        self.trigger_event = tk.StringVar(value=state.trigger_event)
        self.trigger_filter = tk.StringVar(value=state.trigger_filter)
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Collision").pack(side="left", padx=(0, 6))
        for value, label in (("select", "Select"), ("collider", "Collider"), ("trigger", "Trigger")):
            ttk.Radiobutton(self, text=label, value=value, variable=self.tool, command=self.apply).pack(side="left")
        ttk.Label(self, text="Layer").pack(side="left", padx=(12, 4))
        ttk.Entry(self, textvariable=self.collider_layer, width=12).pack(side="left")
        ttk.Label(self, text="Event").pack(side="left", padx=(12, 4))
        ttk.Entry(self, textvariable=self.trigger_event, width=18).pack(side="left")
        ttk.Label(self, text="Filter").pack(side="left", padx=(8, 4))
        ttk.Entry(self, textvariable=self.trigger_filter, width=12).pack(side="left")

    def apply(self) -> None:
        self.state.choose(self.tool.get())
        self.state.collider_layer = self.collider_layer.get().strip() or "default"
        self.state.trigger_event = self.trigger_event.get().strip() or "trigger.enter"
        self.state.trigger_filter = self.trigger_filter.get().strip()
        if self.on_tool_change is not None:
            self.on_tool_change(self.state)

    def sync(self) -> None:
        """Apply editable fields before a canvas gesture starts."""
        self.apply()
