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
        split.add(palette, weight=1)
        split.add(canvas_host, weight=4)

        ttk.Label(palette, text="Node Palette", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(0, 6))
        for kind in self.event_graph_workspace.palette:
            label = kind.replace(".", " / ").replace("_", " ").title()
            ttk.Button(palette, text=label, command=lambda value=kind: self._add_event_node(value)).pack(fill="x", pady=2)
        ttk.Separator(palette).pack(fill="x", pady=8)
        ttk.Button(palette, text="Delete Selected", command=self._delete_event_node).pack(fill="x")

        self.event_graph_canvas_widget = tk.Canvas(canvas_host, background="white", highlightthickness=1)
        self.event_graph_canvas_widget.pack(fill="both", expand=True)
        self.event_graph_canvas = EventGraphCanvas(
            self.event_graph_canvas_widget,
            self.event_graph_workspace.graph,
            on_change=self._event_graph_changed,
            on_select=self.event_graph_workspace.select,
        )
        self.event_graph_canvas.selected_node_id = self.event_graph_workspace.selected_node_id
        self.event_graph_canvas.render()
        self.event_graph_canvas_widget.bind("<ButtonPress-1>", self._event_graph_down)
        self.event_graph_canvas_widget.bind("<B1-Motion>", self._event_graph_move)
        self.event_graph_canvas_widget.bind("<ButtonRelease-1>", self._event_graph_up)

    def _add_event_node(self, kind: str) -> None:
        offset = len(self.event_graph_workspace.graph.nodes) * 24
        self.event_graph_workspace.create_node(kind, 40 + offset, 40 + offset)
        self.activate("event_graph")

    def _delete_event_node(self) -> None:
        if self.event_graph_workspace.delete_selected():
            self.activate("event_graph")

    def _event_graph_down(self, event) -> None:
        self.event_graph_canvas.begin_move(event.x, event.y)

    def _event_graph_move(self, event) -> None:
        self.event_graph_canvas.update_move(event.x, event.y)

    def _event_graph_up(self, event) -> None:
        self.event_graph_canvas.finish_move(event.x, event.y)

    def _event_graph_changed(self) -> None:
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
