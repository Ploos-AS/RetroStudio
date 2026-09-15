"""CreatorShell helpers for mounting Scene Composer collision authoring."""

from __future__ import annotations

from .creator import entity_by_id
from .scene_collision_mount import SceneCollisionMount


def selected_scene_entity(state, scene):
    """Return the currently selected scene entity, if selection is valid."""
    selection = state.selection
    if selection is None or selection.kind != "entity":
        return None
    try:
        return entity_by_id(scene, selection.item_id)
    except ValueError:
        return None


def mount_scene_collision(shell, toolbar_parent, canvas, scene):
    """Mount collision authoring for the selected entity in CreatorShell."""
    entity = selected_scene_entity(shell.state, scene)
    if entity is None:
        return None

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
