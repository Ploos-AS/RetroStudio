from retrostudio.model import Component, Entity
from retrostudio.scene_transform import move_entity, snap


def test_snap_uses_nearest_grid_interval():
    assert snap(19, 8) == 16
    assert snap(21, 8) == 24
    assert snap(33, 16) == 32


def test_move_entity_updates_existing_transform():
    entity = Entity("player", "Player", [Component("transform", {"x": 0, "y": 0})])
    assert move_entity(entity, 37, 50, grid=8) == (40, 48)
    assert entity.components[0].data == {"x": 40, "y": 48}


def test_move_entity_preserves_transform_metadata():
    entity = Entity("npc", "NPC", [Component("transform", {"x": 4, "y": 5, "rotation": 90})])
    move_entity(entity, 64, 72)
    assert entity.components[0].data == {"x": 64, "y": 72, "rotation": 90}


def test_move_entity_requires_transform():
    entity = Entity("logic", "Logic")
    try:
        move_entity(entity, 10, 10)
    except ValueError as exc:
        assert "no transform" in str(exc)
    else:
        raise AssertionError("missing transform should fail")
