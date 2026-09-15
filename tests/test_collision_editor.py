from retrostudio.collision_editor import (
    apply_box_collider,
    apply_box_trigger,
    apply_circle_collider,
    box_from_drag,
    overlays_for_entity,
    paint_box,
    remove_collision,
    resize_box,
    resize_box_from_scene,
)
from retrostudio.model import Component, Entity


def entity_at(x=100, y=50):
    return Entity("player", "Player", [Component("transform", {"x": x, "y": y})])


def test_box_collider_overlay_uses_scene_coordinates():
    entity = entity_at()
    apply_box_collider(entity, 4, 6, 32, 18, layer="player")
    overlay = overlays_for_entity(entity)[0]
    assert overlay.kind == "collider"
    assert overlay.shape == "box"
    assert (overlay.x, overlay.y, overlay.width, overlay.height) == (104, 56, 32, 18)
    assert overlay.label == "player"


def test_circle_collider_overlay():
    entity = entity_at()
    apply_circle_collider(entity, 8, 9, 12)
    overlay = overlays_for_entity(entity)[0]
    assert overlay.shape == "circle"
    assert (overlay.x, overlay.y, overlay.radius) == (108, 59, 12)


def test_trigger_overlay_carries_event_label():
    entity = entity_at()
    apply_box_trigger(entity, 0, 0, 64, 32, "door.open", "player")
    overlay = overlays_for_entity(entity)[0]
    assert overlay.kind == "trigger"
    assert overlay.label == "door.open"


def test_drag_is_normalized_and_entity_local():
    entity = entity_at()
    shape = box_from_drag(entity, 150, 90, 110, 60)
    assert (shape.x, shape.y, shape.width, shape.height) == (10, 10, 40, 30)


def test_paint_box_creates_scene_overlay():
    entity = entity_at()
    paint_box(entity, "collider", 104, 56, 140, 80, label="player")
    overlay = overlays_for_entity(entity)[0]
    assert (overlay.x, overlay.y, overlay.width, overlay.height) == (104, 56, 36, 24)
    assert overlay.label == "player"


def test_resize_box_converts_scene_to_local():
    entity = entity_at()
    shape = resize_box_from_scene(entity, 120, 70, 48, 20)
    assert (shape.x, shape.y, shape.width, shape.height) == (20, 20, 48, 20)


def test_resize_collider_preserves_metadata():
    entity = entity_at()
    apply_box_collider(entity, 4, 6, 32, 18, layer="player", solid=False)
    resize_box(entity, "collider", 120, 70, 48, 20)
    component = next(component for component in entity.components if component.type == "collision.collider")
    overlay = overlays_for_entity(entity)[0]
    assert (overlay.x, overlay.y, overlay.width, overlay.height) == (120, 70, 48, 20)
    assert component.data["layer"] == "player"
    assert component.data["solid"] is False


def test_resize_trigger_preserves_event_and_filter():
    entity = entity_at()
    apply_box_trigger(entity, 0, 0, 32, 32, "door.open", "player")
    resize_box(entity, "trigger", 110, 60, 50, 25)
    component = next(component for component in entity.components if component.type == "collision.trigger")
    overlay = overlays_for_entity(entity)[0]
    assert (overlay.x, overlay.y, overlay.width, overlay.height) == (110, 60, 50, 25)
    assert component.data["event"] == "door.open"
    assert component.data["filter_tag"] == "player"


def test_remove_collision_only_removes_requested_kind():
    entity = entity_at()
    apply_box_collider(entity, 0, 0, 16, 16)
    apply_box_trigger(entity, 0, 0, 32, 32, "enter")
    remove_collision(entity, "collider")
    overlays = overlays_for_entity(entity)
    assert len(overlays) == 1
    assert overlays[0].kind == "trigger"


def test_invalid_sizes_are_rejected():
    entity = entity_at()
    try:
        apply_box_collider(entity, 0, 0, 0, 16)
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        raise AssertionError("invalid collider was accepted")
