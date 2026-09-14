"""Tk creator panel for adding and editing reusable behaviours."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from .behaviour_editor import add_from_editor, editor_fields, editor_state, remove_from_editor, update_from_editor
from .behaviours import BehaviourDefinition
from .model import Entity


class BehaviourPanel(ttk.LabelFrame):
    """Schema-driven creator UI; no raw component JSON is exposed."""

    def __init__(
        self,
        parent,
        entity: Entity,
        on_change: Callable[[], None] | None = None,
        on_status: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(parent, text="Behaviours", padding=10)
        self.entity = entity
        self.on_change = on_change or (lambda: None)
        self.on_status = on_status or (lambda _message: None)
        self.selected = tk.StringVar()
        self.add_choice = tk.StringVar()
        self.variables: dict[str, tk.Variable] = {}
        self._build()

    def _build(self) -> None:
        for child in self.winfo_children():
            child.destroy()

        state = editor_state(self.entity)
        attached_names = [item.behaviour_type for item in state.attached]
        available_to_add = [name for name in state.available if name not in attached_names]

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 8))
        add_box = ttk.Combobox(toolbar, textvariable=self.add_choice, values=available_to_add, state="readonly", width=24)
        add_box.pack(side="left")
        if available_to_add:
            self.add_choice.set(available_to_add[0])
        ttk.Button(toolbar, text="Add Behaviour", command=self._add).pack(side="left", padx=6)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body, padding=(0, 0, 8, 0))
        right = ttk.Frame(body)
        body.add(left, weight=1)
        body.add(right, weight=3)

        self.listbox = tk.Listbox(left, exportselection=False, height=8)
        self.listbox.pack(fill="both", expand=True)
        for definition in state.attached:
            self.listbox.insert("end", definition.behaviour_type)
        self.listbox.bind("<<ListboxSelect>>", lambda _event: self._select_from_list())

        if state.attached:
            current = self.selected.get()
            index = 0
            if current in attached_names:
                index = attached_names.index(current)
            self.listbox.selection_set(index)
            self.selected.set(attached_names[index])
            self._render_editor(right, state.attached[index])
        else:
            ttk.Label(right, text="Add a behaviour to give this object game logic without scripting.", wraplength=520).pack(anchor="nw")

    def _select_from_list(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        self.selected.set(str(self.listbox.get(selection[0])))
        self._build()

    def _render_editor(self, parent, definition: BehaviourDefinition) -> None:
        values = definition.normalized_values()
        self.variables = {}
        ttk.Label(parent, text=definition.behaviour_type, font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(0, 8))
        form = ttk.Frame(parent)
        form.pack(fill="x")

        row = 0
        for field in editor_fields(definition.behaviour_type):
            ttk.Label(form, text=field.label).grid(row=row, column=0, sticky="nw", padx=(0, 8), pady=4)
            value = values[field.key]
            if field.field_type == "boolean":
                variable = tk.BooleanVar(value=bool(value))
                ttk.Checkbutton(form, variable=variable).grid(row=row, column=1, sticky="w", pady=4)
            elif field.field_type == "choice":
                variable = tk.StringVar(value=str(value))
                ttk.Combobox(form, textvariable=variable, values=field.choices, state="readonly", width=24).grid(row=row, column=1, sticky="ew", pady=4)
            elif field.field_type == "multiline":
                variable = tk.StringVar(value=str(value))
                text = tk.Text(form, width=48, height=5, wrap="word")
                text.insert("1.0", str(value))
                text.grid(row=row, column=1, sticky="ew", pady=4)
                text.bind("<KeyRelease>", lambda _event, widget=text, var=variable: var.set(widget.get("1.0", "end-1c")))
            else:
                variable = tk.StringVar(value=str(value))
                ttk.Entry(form, textvariable=variable, width=32).grid(row=row, column=1, sticky="ew", pady=4)
            self.variables[field.key] = variable
            row += 1

        actions = ttk.Frame(parent)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Apply Behaviour", command=self._apply).pack(side="left")
        ttk.Button(actions, text="Remove", command=self._remove).pack(side="left", padx=6)
        form.columnconfigure(1, weight=1)

    def _raw_values(self) -> dict[str, object]:
        return {key: variable.get() for key, variable in self.variables.items()}

    def _add(self) -> None:
        behaviour = self.add_choice.get().strip()
        if not behaviour:
            self.on_status("Choose a behaviour first.")
            return
        try:
            add_from_editor(self.entity, behaviour)
        except (TypeError, ValueError) as exc:
            self.on_status(f"Could not add behaviour: {exc}")
            return
        self.selected.set(behaviour)
        self.on_change()
        self.on_status(f"Added {behaviour}")
        self._build()

    def _apply(self) -> None:
        behaviour = self.selected.get().strip()
        if not behaviour:
            return
        try:
            update_from_editor(self.entity, behaviour, self._raw_values())
        except (TypeError, ValueError) as exc:
            self.on_status(f"Could not update behaviour: {exc}")
            return
        self.on_change()
        self.on_status(f"Updated {behaviour}")
        self._build()

    def _remove(self) -> None:
        behaviour = self.selected.get().strip()
        if not behaviour:
            return
        if remove_from_editor(self.entity, behaviour):
            self.selected.set("")
            self.on_change()
            self.on_status(f"Removed {behaviour}")
            self._build()
