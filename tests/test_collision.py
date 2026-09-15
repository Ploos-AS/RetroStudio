from retrostudio.collision import (
    COLLIDER_COMPONENT,
    TRIGGER_COMPONENT,
    CollisionShape,
    collision_diagnostics,
    set_collider,
    set_trigger,
)
from retrostudio.model import Entity


def test_box_shape_round_trip():
    shape = CollisionShape(shape="box", x=2, y=3, width=32, height=12)
    assert CollisionShape.from_dict(shape.to_dict()) == shape
    assert shape.diagnostics() == []


def test_circle_shape_round_trip():
    shape = CollisionShape(shape="circle", x=4, y=5, radius=7)
    restored = CollisionShape.from_dict(shape.to_dict())
    assert restored.shape == "circle"
    assert restored.radius == 7
    assert restored.diagnostics() == []


def test_set_collider_is_stable_component_update():
    entity = Entity("player", "Player")
    set_collider(entity, CollisionShape(width=16, height=24), layer="actors")
    set_collider(entity, CollisionShape(width=18, height=26), layer="actors")
    colliders = [c for c in entity.components if c.type == COLLIDER_COMPONENT]
    assert len(colliders) == 1
    assert colliders[0].data["shape"]["width"] == 18


def test_trigger_requires_event():
    entity = Entity("door", "Door")
    set_trigger(entity, CollisionShape(width=20, height=30), event="")
    assert entity.components[0].type == TRIGGER_COMPONENT
    assert [d.code for d in collision_diagnostics(entity)] == ["collision.trigger_event"]


def test_invalid_shapes_report_creator_safe_diagnostics():
    entity = Entity("bad", "Bad")
    set_collider(entity, CollisionShape(shape="box", width=0, height=10))
    set_trigger(entity, CollisionShape(shape="circle", radius=-1), event="enter")
    assert [d.code for d in collision_diagnostics(entity)] == [
        "collision.box_size",
        "collision.circle_radius",
    ]
