"""Tk adapter for Scene Composer grid, snap modes and keyboard movement."""

from __future__ import annotations


def mount_scene_grid(shell, parent, canvas, scene, selected_entity) -> None:
    import tkinter as tk
    from tkinter import ttk

    from .model import save_project
    from .scene_transform import GRID_SIZES, nudge_entity

    row = ttk.Frame(parent)
    row.pack(fill="x", pady=(0, 6))
    ttk.Label(row, text="Grid:").pack(side="left")
    labels = {0: "Off", 8: "8 px", 16: "16 px", 32: "32 px"}
    grid_var = tk.StringVar(value=labels.get(shell.scene_grid_size, "8 px"))

    def draw_grid(_event=None) -> None:
        canvas.delete("scene-grid")
        grid = shell.scene_grid_size
        if grid <= 0:
            return
        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), 1)
        for x in range(grid, width, grid):
            canvas.create_line(x, 0, x, height, tags=("scene-grid",), stipple="gray75")
        for y in range(grid, height, grid):
            canvas.create_line(0, y, width, y, tags=("scene-grid",), stipple="gray75")
        canvas.tag_lower("scene-grid")

    def choose_grid(_event=None) -> None:
        reverse = {label: size for size, label in labels.items()}
        shell.scene_grid_size = reverse[grid_var.get()]
        draw_grid()
        mode = "off" if shell.scene_grid_size == 0 else f"{shell.scene_grid_size}px"
        shell.status.set(f"Scene snap grid: {mode}")

    chooser = ttk.Combobox(row, width=7, state="readonly", textvariable=grid_var, values=[labels[size] for size in GRID_SIZES])
    chooser.pack(side="left", padx=(5, 10))
    chooser.bind("<<ComboboxSelected>>", choose_grid)
    ttk.Label(row, text="Arrow keys nudge selected object by one grid step.").pack(side="left")

    def nudge(dx: int, dy: int):
        entity = selected_entity()
        if entity is None:
            return None
        try:
            x, y = nudge_entity(entity, dx, dy, grid=shell.scene_grid_size)
        except ValueError:
            return None
        project = shell.state.project
        if project.source_path:
            save_project(project, project.source_path)
            shell.status.set(f"Moved {entity.name} to {x}, {y} — project saved")
        else:
            shell.status.set(f"Moved {entity.name} to {x}, {y} — save project to persist")
        shell.activate("scene")
        return "break"

    canvas.bind("<Left>", lambda _event: nudge(-1, 0), add="+")
    canvas.bind("<Right>", lambda _event: nudge(1, 0), add="+")
    canvas.bind("<Up>", lambda _event: nudge(0, -1), add="+")
    canvas.bind("<Down>", lambda _event: nudge(0, 1), add="+")
    canvas.bind("<Configure>", draw_grid, add="+")
    canvas.bind("<Button-1>", lambda _event: canvas.focus_set(), add="+")
    canvas.after_idle(draw_grid)
