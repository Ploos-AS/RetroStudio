"""CreatorShell helpers for mounting Scene Composer creator tools."""

from __future__ import annotations

from .creator import entity_by_id


def selected_scene_entity(state, scene):
    """Return the currently selected scene entity, if selection is valid."""
    selection = state.selection
    if selection is None or selection.kind != "entity":
        return None
    try:
        return entity_by_id(scene, selection.item_id)
    except ValueError:
        return None


def _mount_prefab_browser(shell, toolbar_parent, scene) -> None:
    """Add creator templates with preview/configuration before placement."""
    import tkinter as tk
    from tkinter import ttk
    from .prefab_browser import PrefabBrowser

    browser = PrefabBrowser()
    row = ttk.Frame(toolbar_parent)
    row.pack(fill="x", pady=(0, 6))
    ttk.Label(row, text="Templates:").pack(side="left")
    button = ttk.Menubutton(row, text="Add Template…")
    menu = tk.Menu(button, tearoff=False)

    def configure(prefab_id: str) -> None:
        definition = browser.definition(prefab_id)
        preview = browser.preview(prefab_id)
        dialog = tk.Toplevel(shell.root)
        dialog.title(f"Add {definition.name}")
        dialog.transient(shell.root)
        body = ttk.Frame(dialog, padding=12)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=definition.name, font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(body, text=definition.description, wraplength=420).pack(anchor="w", pady=(3, 8))
        preview_canvas = tk.Canvas(body, width=420, height=130, background="white", highlightthickness=1)
        preview_canvas.pack(fill="x", pady=(0, 8))
        scale = min(3.0, 88.0 / max(preview.width, preview.height, 1.0))
        width, height = preview.width * scale, preview.height * scale
        cx, cy = 85.0, 65.0
        if preview.collision_shape == "circle":
            preview_canvas.create_oval(cx-width/2, cy-height/2, cx+width/2, cy+height/2, width=2)
        else:
            preview_canvas.create_rectangle(cx-width/2, cy-height/2, cx+width/2, cy+height/2, width=2)
        preview_canvas.create_text(155, 28, anchor="nw", text=f"Footprint: {preview.width:g} × {preview.height:g}")
        preview_canvas.create_text(155, 52, anchor="nw", text=f"Collision: {preview.collision_shape or 'none'}")
        preview_canvas.create_text(155, 76, anchor="nw", text="Features: " + (", ".join(preview.features) or "none"), width=245)
        ttk.Label(body, text=f"Genre: {definition.genre.title()}").pack(anchor="w", pady=(0, 8))
        ttk.Label(body, text="Object name").pack(anchor="w")
        name_var = tk.StringVar(value=definition.name)
        ttk.Entry(body, textvariable=name_var, width=42).pack(fill="x", pady=(1, 8))
        variables = {}
        for field in browser.fields(prefab_id):
            ttk.Label(body, text=field.label).pack(anchor="w")
            if field.field_type == "boolean":
                variable = tk.BooleanVar(value=bool(field.value))
                ttk.Checkbutton(body, variable=variable).pack(anchor="w", pady=(1, 7))
            else:
                variable = tk.StringVar(value=str(field.value if field.value is not None else ""))
                if field.field_type == "choice":
                    ttk.Combobox(body, textvariable=variable, values=field.choices, state="readonly").pack(fill="x", pady=(1, 7))
                else:
                    ttk.Entry(body, textvariable=variable).pack(fill="x", pady=(1, 7))
            variables[(field.component_type, field.key)] = (field, variable)

        def convert(field, value):
            if field.field_type == "number":
                text = str(value).strip()
                return float(text) if "." in text else int(text)
            return value

        def place() -> None:
            try:
                values = {key: convert(field, variable.get()) for key, (field, variable) in variables.items()}
            except ValueError:
                shell.status.set("Template value must be a valid number")
                return
            offset = (len(scene.entities) % 8) * 24
            entity = browser.place(scene, prefab_id, x=64 + offset, y=64 + offset, name=name_var.get(), values=values)
            shell.state.select("entity", entity.entity_id)
            project = shell.state.project
            if project.source_path:
                from .model import save_project
                save_project(project, project.source_path)
                shell.status.set(f"Added {entity.name} template — project saved")
            else:
                shell.status.set(f"Added {entity.name} template — save project to persist")
            dialog.destroy()
            shell.activate("scene")

        actions = ttk.Frame(body)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Add to Scene", command=place).pack(side="right")
        ttk.Button(actions, text="Cancel", command=dialog.destroy).pack(side="right", padx=(0, 6))

    for genre in browser.genres:
        genre_menu = tk.Menu(menu, tearoff=False)
        for definition in browser.items(genre):
            genre_menu.add_command(label=definition.name, command=lambda prefab_id=definition.prefab_id: configure(prefab_id))
        menu.add_cascade(label=genre.title(), menu=genre_menu)
    button.configure(menu=menu)
    button.pack(side="left", padx=(6, 0))
    ttk.Label(row, text="Preview and tune reusable gameplay objects before placing them.").pack(side="left", padx=10)


def mount_scene_collision(shell, toolbar_parent, canvas, scene):
    """Mount Scene Composer templates plus collision authoring."""
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

    mount = SceneCollisionMount(toolbar_parent, canvas, entity, on_change=changed, on_status=shell.status.set)
    mount.mount()
    return mount
