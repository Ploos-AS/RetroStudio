from retrostudio.model import Entity, Project, Scene
from retrostudio.scene_collision_desktop import selected_scene_entity
from retrostudio.workspace import WorkspaceState


def project_with_entity():
    entity = Entity("player", "Player", [])
    scene = Scene("main", "Main", [entity])
    return Project("Game", "game", "", [scene]), scene, entity


def test_selected_scene_entity_returns_current_entity():
    project, scene, entity = project_with_entity()
    state = WorkspaceState(project)
    state.select("entity", "player")
    assert selected_scene_entity(state, scene) is entity


def test_selected_scene_entity_ignores_non_entity_selection():
    project, scene, _ = project_with_entity()
    state = WorkspaceState(project)
    state.select("asset", "hero.png")
    assert selected_scene_entity(state, scene) is None


def test_selected_scene_entity_handles_stale_selection():
    project, scene, _ = project_with_entity()
    state = WorkspaceState(project)
    state.select("entity", "missing")
    assert selected_scene_entity(state, scene) is None
