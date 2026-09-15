"""Reusable Tk collision/trigger editor panel for the native creator shell."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .collision_editor import apply_box_collider, apply_box_trigger, apply_circle_collider, remove_collision


class CollisionEditorPanel(ttk.LabelFrame):
    def __init__(self, parent, entity, on_change=None):
        super().__init__(parent, text="Collision & Triggers", padding=8)
        self.entity = entity
        self.on_change = on_change
        self.shape = tk.StringVar(value="box")
        self.x = tk.StringVar(value="0")
        self.y = tk.StringVar(value="0")
        self.width = tk.StringVar(value="96")
        self.height = tk.StringVar(value="48")
        self.radius = tk.StringVar(value="24")
        self.layer = tk.StringVar(value="default")
        self.solid = tk.BooleanVar(value=True)
        self.event = tk.StringVar(value="trigger.enter")
        self.filter_tag = tk.StringVar(value="")
        self.message = tk.StringVar(value="Draw a collider or trigger around this object.")
        self._build()

    def _build(self):
        ttk.Label(self, text="Shape").grid(row=0, column=0, sticky="w")
        ttk.Combobox(self, textvariable=self.shape, values=("box", "circle"), state="readonly", width=12).grid(row=0, column=1, sticky="w")
        fields = (("Offset X", self.x), ("Offset Y", self.y), ("Width", self.width), ("Height", self.height), ("Radius", self.radius), ("Layer", self.layer))
        for row, (label, variable) in enumerate(fields, start=1):
            ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(self, textvariable=variable, width=18).grid(row=row, column=1, sticky="w", pady=2)
        ttk.Checkbutton(self, text="Solid collider", variable=self.solid).grid(row=7, column=1, sticky="w")
        ttk.Label(self, text="Trigger event").grid(row=8, column=0, sticky="w", pady=2)
        ttk.Entry(self, textvariable=self.event, width=24).grid(row=8, column=1, sticky="w", pady=2)
        ttk.Label(self, text="Filter tag").grid(row=9, column=0, sticky="w", pady=2)
        ttk.Entry(self, textvariable=self.filter_tag, width=24).grid(row=9, column=1, sticky="w", pady=2)
        buttons = ttk.Frame(self)
        buttons.grid(row=10, column=0, columnspan=2, sticky="w", pady=(8, 2))
        ttk.Button(buttons, text="Apply Collider", command=self.apply_collider).pack(side="left")
        ttk.Button(buttons, text="Apply Trigger", command=self.apply_trigger).pack(side="left", padx=4)
        ttk.Button(buttons, text="Remove Collider", command=lambda: self.remove("collider")).pack(side="left", padx=4)
        ttk.Button(buttons, text="Remove Trigger", command=lambda: self.remove("trigger")).pack(side="left")
        ttk.Label(self, textvariable=self.message, wraplength=460).grid(row=11, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _numbers(self):
        return float(self.x.get()), float(self.y.get()), float(self.width.get()), float(self.height.get()), float(self.radius.get())

    def apply_collider(self):
        try:
            x, y, width, height, radius = self._numbers()
            if self.shape.get() == "circle":
                apply_circle_collider(self.entity, x, y, radius, self.layer.get(), self.solid.get())
            else:
                apply_box_collider(self.entity, x, y, width, height, self.layer.get(), self.solid.get())
        except ValueError as exc:
            self.message.set(str(exc))
            return
        self.message.set("Collider updated. Scene overlay will use the canonical shape.")
        self._changed()

    def apply_trigger(self):
        try:
            x, y, width, height, _radius = self._numbers()
            if self.shape.get() != "box":
                raise ValueError("circle triggers are not exposed by this first editor slice")
            apply_box_trigger(self.entity, x, y, width, height, self.event.get(), self.filter_tag.get())
        except ValueError as exc:
            self.message.set(str(exc))
            return
        self.message.set("Trigger updated.")
        self._changed()

    def remove(self, kind):
        remove_collision(self.entity, kind)
        self.message.set(f"{kind.title()} removed.")
        self._changed()

    def _changed(self):
        if self.on_change is not None:
            self.on_change()
