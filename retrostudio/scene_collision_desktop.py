"""CreatorShell helpers for mounting Scene Composer creator tools."""

from __future__ import annotations

from .creator import entity_by_id


def selected_scene_entity(state, scene):
    """Return the currently selected scene entity, if selection is valid.

    This helper deliberately stays GUI-toolkit independent so model/controller
    tests can run on headless builders without Tk installed.
    """
    selection = state.selection
    if selection is None or selection.kind != "entity":
        return None
    try:
        return entity_by_id(scene, selection.item_id)
    except ValueError:
        return None


def _mount_prefab_browser(shell, toolbar_parent, scene) -> None:
    """Add a compact creator-template menu above the Scene Composer canvas."""
    import tkinter as tk
    from tkinter import ttk

    from .prefab_browser import PrefabBrowser

    browser = PrefabBrowser()
    row = ttk.Frame(toolbar_parent)
    row.pack(fill="x", pady=(0, 6))
    ttk.Label(row, text="Templates:").pack(side="left")
    button = ttk.Menubutton(row, text="Add Template…")
    menu = tk.Menu(button, tearoff=False)

    def place(prefab_id: str) -> None:
        offset = (len(scene.entities) % 8) * 24
        entity = browser.place(scene, prefab_id, x=64 + offset, y=64 + offset)
        shell.state.select("entity", entity.entity_id)
        project = shell.state.project
        if project.source_path:
            from .model import save_project

            save_project(project, project.source_path)
            shell.status.set(f"Added {entity.name} template — project saved")
        else:
            shell.status.set(f"Added {entity.name} template — save project to persist")
        shell.activate("scene")

    for genre in browser.genres:
        genre_menu = tk.Menu(menu, tearoff=False)
        for definition in browser.items(genre):
            genre_menu.add_command(
                label=definition.name,
                command=lambda prefab_id=definition.prefab_id: place(prefab_id),
            )
        menu.add_cascade(label=genre.title(), menu=genre_menu)
    button.configure(menu=menu)
    button.pack(side="left", padx=(6, 0))
    ttk.Label(row, text="Start from reusable gameplay objects, then replace artwork and tune properties.").pack(side="left", padx=10)


def mount_scene_collision(shell, toolbar_parent, canvas, scene):
    """Mount Scene Composer templates plus collision authoring.

    Tk-backed creator tools are imported lazily so importing this module for
    headless selection tests does not require tkinter.
    """
    _mount_prefab_browser(shell, toolbar_parent, scene)
    entity = selected_scene_entity(shell.state, scene)
    if entity is None:
        return None

    from .scene_collision_mount import SceneCollisionMount

    def changed():
        project = shell.state.project
        if project.source_path:
            from .model import save_project

            save_project(project, project.source_path)
            shell.status.set(f"Collision updated for {entity.name} — project saved")
        else:
            shell.status.set(f"Collision updated for {entity.name} — save project to persist")

    mount = SceneCollisionMount(
        toolbar_parent,
        canvas,
        entity,
        on_change=changed,
        on_status=shell.status.set,
    )
    mount.mount()
    return mount
