"""Native RetroStudio creator shell with collision and event-graph authoring."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .desktop_base import CreatorShell as _BaseCreatorShell, WORKSPACE_LABELS
from .event_graph_canvas import EventGraphCanvas
from .event_graph_workspace import EventGraphWorkspace
from .scene_collision_desktop import mount_scene_collision

WORKSPACE_LABELS["event_graph"] = "Event Graph"


class CreatorShell(_BaseCreatorShell):
    """Creator shell with visual collision and event-graph authoring."""

    def __init__(self, root, project=None) -> None:
        self.event_graph_workspace = EventGraphWorkspace(on_change=self._event_graph_changed)
        super().__init__(root, project)

    def activate(self, workspace: str) -> None:
        if workspace == "event_graph":
            self.state.activate(workspace)
            self.workspace_title.set(WORKSPACE_LABELS[workspace])
            self.subtitle.configure(text="Build game behaviour visually from events, conditions and actions.")
            for child in self.workspace_frame.winfo_children():
                child.destroy()
            self._render_event_graph()
            self.status.set(f"{self.state.project.name} — {WORKSPACE_LABELS[workspace]}")
            return
        super().activate(workspace)

    def _render_event_graph(self) -> None:
        split = ttk.Panedwindow(self.workspace_frame, orient="horizontal")
        split.pack(fill="both", expand=True)
        palette = ttk.Frame(split, padding=6)
        canvas_host = ttk.Frame(split, padding=6)
        inspector = ttk.Frame(split, padding=6)
        split.add(palette, weight=1)
        split.add(canvas_host, weight=4)
        split.add(inspector, weight=2)
        ttk.Label(palette, text="Node Palette", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(0, 6))
        for kind in self.event_graph_workspace.palette:
            label = kind.replace(".", " / ").replace("_", " ").title()
            ttk.Button(palette, text=label, command=lambda value=kind: self._add_event_node(value)).pack(fill="x", pady=2)
        ttk.Separator(palette).pack(fill="x", pady=8)
        ttk.Button(palette, text="Delete Selected", command=self._delete_event_node).pack(fill="x")
        self.event_graph_canvas_widget = tk.Canvas(canvas_host, background="white", highlightthickness=1)
        self.event_graph_canvas_widget.pack(fill="both", expand=True)
        self.event_graph_canvas = EventGraphCanvas(self.event_graph_canvas_widget, self.event_graph_workspace.graph, on_change=self._event_graph_changed, on_select=self._event_graph_selected)
        self.event_graph_canvas.selected_node_id = self.event_graph_workspace.selected_node_id
        self.event_graph_canvas.render()
        self.event_graph_canvas_widget.bind("<ButtonPress-1>", self._event_graph_down)
        self.event_graph_canvas_widget.bind("<B1-Motion>", self._event_graph_move)
        self.event_graph_canvas_widget.bind("<ButtonRelease-1>", self._event_graph_up)
        self._render_event_graph_inspector(inspector)

    def _render_event_graph_inspector(self, parent) -> None:
        ttk.Label(parent, text="Node Inspector", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(0, 8))
        node = self.event_graph_workspace.selected_node
        if node is None:
            ttk.Label(parent, text="Select a node to edit its properties.", wraplength=220).pack(anchor="w")
            return
        ttk.Label(parent, text=node.kind.replace(".", " / ").replace("_", " ").title()).pack(anchor="w")
        ttk.Label(parent, text=node.node_id).pack(anchor="w", pady=(0, 10))
        for name in self.event_graph_workspace.editable_properties():
            ttk.Label(parent, text=name.replace("_", " ").title()).pack(anchor="w")
            variable = tk.StringVar(value=str(node.data.get(name, "")))
            entry = ttk.Entry(parent, textvariable=variable)
            entry.pack(fill="x", pady=(1, 7))
            entry.bind("<Return>", lambda _event, key=name, var=variable: self._set_event_graph_property(key, var.get()))
            entry.bind("<FocusOut>", lambda _event, key=name, var=variable: self._set_event_graph_property(key, var.get()))
        diagnostics = [item for item in self.event_graph_workspace.graph.diagnostics() if node.node_id in item.path]
        if diagnostics:
            ttk.Separator(parent).pack(fill="x", pady=8)
            for item in diagnostics:
                ttk.Label(parent, text=item.message, wraplength=220).pack(anchor="w", pady=2)

    def _set_event_graph_property(self, name: str, value: str) -> None:
        if self.event_graph_workspace.set_property(name, value):
            self.event_graph_canvas.render()

    def _event_graph_selected(self, node_id: str | None) -> None:
        self.event_graph_workspace.select(node_id)
        self.activate("event_graph")

    def _add_event_node(self, kind: str) -> None:
        offset = len(self.event_graph_workspace.graph.nodes) * 24
        self.event_graph_workspace.create_node(kind, 40 + offset, 40 + offset)
        self.activate("event_graph")

    def _delete_event_node(self) -> None:
        if self.event_graph_workspace.delete_selected():
            self.activate("event_graph")

    def _event_graph_down(self, event) -> None:
        self.event_graph_canvas.begin_gesture(event.x, event.y)

    def _event_graph_move(self, event) -> None:
        self.event_graph_canvas.update_gesture(event.x, event.y)

    def _event_graph_up(self, event) -> None:
        self.event_graph_canvas.finish_gesture(event.x, event.y)

    def _event_graph_changed(self) -> None:
        if hasattr(self, "status"):
            self.status.set("Event Graph updated")

    def _render_scene(self) -> None:
        split = ttk.Panedwindow(self.workspace_frame, orient="horizontal")
        split.pack(fill="both", expand=True)
        entities_frame = ttk.Frame(split, padding=6)
        canvas_frame = ttk.Frame(split, padding=6)
        split.add(entities_frame, weight=1)
        split.add(canvas_frame, weight=4)
        ttk.Label(entities_frame, text="Scene Objects", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        entity_list = tk.Listbox(entities_frame, exportselection=False)
        entity_list.pack(fill="both", expand=True, pady=(6, 0))
        scene = self._active_scene()
        if scene is None:
            ttk.Label(canvas_frame, text="This project has no scene yet.").pack(anchor="center", expand=True)
            return
        for entity in scene.entities:
            entity_list.insert("end", f"{entity.name}  [{entity.entity_id}]")
        entity_list.bind("<<ListboxSelect>>", lambda _event: self._select_scene_entity(entity_list, scene))
        current_id = self.state.selection.item_id if self.state.selection and self.state.selection.kind == "entity" else None
        if current_id:
            for index, entity in enumerate(scene.entities):
                if entity.entity_id == current_id:
                    entity_list.selection_set(index)
                    entity_list.see(index)
                    break
        collision_host = ttk.Frame(canvas_frame)
        collision_host.pack(fill="x")
        self.scene_canvas = tk.Canvas(canvas_frame, background="white", highlightthickness=1)
        self.scene_canvas.pack(fill="both", expand=True)
        self.scene_canvas.create_text(16, 16, anchor="nw", text=scene.name, font=("TkDefaultFont", 12, "bold"))
        for entity in scene.entities:
            position = self._entity_position(entity)
            visual = self._entity_asset(entity)
            if position is None:
                continue
            x, y = position
            label = Path(visual).name if visual else entity.name
            tag = f"entity:{entity.entity_id}"
            self.scene_canvas.create_rectangle(x, y, x + 96, y + 48, tags=(tag,))
            self.scene_canvas.create_text(x + 48, y + 24, text=label, width=88, tags=(tag,))
            self.scene_canvas.tag_bind(tag, "<Button-1>", lambda _event, eid=entity.entity_id: self._select_scene_entity_id(eid))
            self.scene_canvas.tag_bind(tag, "<Double-Button-1>", lambda _event, eid=entity.entity_id: self._select_entity_and_inspect(eid))
        self.scene_collision_mount = mount_scene_collision(self, collision_host, self.scene_canvas, scene)
        if self.scene_collision_mount is None:
            ttk.Label(collision_host, text="Select a scene object to edit collision and triggers.").pack(anchor="w", pady=(0, 6))

    def _select_scene_entity(self, widget: tk.Listbox, scene) -> None:
        selection = widget.curselection()
        if not selection:
            return
        self._select_scene_entity_id(scene.entities[selection[0]].entity_id)

    def _select_scene_entity_id(self, entity_id: str) -> None:
        self.state.select("entity", entity_id)
        self.activate("scene")


def main() -> None:
    root = tk.Tk()
    CreatorShell(root)
    root.mainloop()


if __name__ == "__main__":
    main()
