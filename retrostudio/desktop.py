"""Native RetroStudio creator shell with Scene Composer collision authoring."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from .desktop_base import CreatorShell as _BaseCreatorShell
from .scene_collision_desktop import mount_scene_collision


class CreatorShell(_BaseCreatorShell):
    """Creator shell with collision painting mounted into Scene Composer."""

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
