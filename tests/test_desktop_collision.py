from retrostudio.desktop_collision import CollisionToolState, SceneCollisionController
from retrostudio.collision_editor import apply_box_collider, apply_box_trigger, apply_circle_collider, overlays_for_entity
from retrostudio.model import Component, Entity


class Event:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Canvas:
    def __init__(self):
        self.bindings = []
        self.items = []

    def bind(self, event, callback, add=None):
        self.bindings.append((event, callback, add))

    def delete(self, tag):
        self.items = [item for item in self.items if tag not in item[-1]]

    def create_rectangle(self, *args, **kwargs):
        self.items.append(("rectangle", args, kwargs, kwargs.get("tags", ())))
        return len(self.items)

    def create_oval(self, *args, **kwargs):
        self.items.append(("oval", args, kwargs, kwargs.get("tags", ())))
        return len(self.items)

    def create_text(self, *args, **kwargs):
        self.items.append(("text", args, kwargs, kwargs.get("tags", ())))
        return len(self.items)


def entity():
    return Entity("player", "Player", [Component("transform", {"x": 100, "y": 50})])


def test_tool_state_validates_modes():
    state = CollisionToolState()
    state.choose("collider")
    assert state.painting
    state.choose("select")
    assert not state.painting


def test_controller_binds_pointer_gestures():
    canvas = Canvas()
    controller = SceneCollisionController(canvas, entity())
    controller.bind()
    assert [event for event, _, _ in canvas.bindings] == ["<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"]


def test_collider_drag_updates_entity_and_calls_change():
    canvas = Canvas()
    changed = []
    state = CollisionToolState(tool="collider", collider_layer="player")
    target = entity()
    controller = SceneCollisionController(canvas, target, state, lambda: changed.append(True))
    controller.pointer_down(Event(104, 56))
    controller.pointer_move(Event(140, 80))
    controller.pointer_up(Event(140, 80))
    collision = next(component for component in target.components if component.type == "collision.collider")
    assert collision.data["layer"] == "player"
    assert collision.data["shape"]["width"] == 36
    assert collision.data["shape"]["height"] == 24
    assert changed == [True]


def test_trigger_drag_uses_event_and_filter():
    canvas = Canvas()
    state = CollisionToolState(tool="trigger", trigger_event="door.open", trigger_filter="player")
    target = entity()
    controller = SceneCollisionController(canvas, target, state)
    controller.pointer_down(Event(100, 50))
    controller.pointer_up(Event(132, 82))
    trigger = next(component for component in target.components if component.type == "collision.trigger")
    assert trigger.data["event"] == "door.open"
    assert trigger.data["filter_tag"] == "player"


def test_se_handle_resizes_collider_and_preserves_metadata():
    canvas = Canvas()
    changed = []
    target = entity()
    apply_box_collider(target, 0, 0, 32, 20, layer="player", solid=False)
    controller = SceneCollisionController(canvas, target, on_change=lambda: changed.append(True))
    controller.render()
    controller.pointer_down(Event(132, 70))
    controller.pointer_move(Event(150, 82))
    controller.pointer_up(Event(150, 82))
    overlay = overlays_for_entity(target)[0]
    collision = next(component for component in target.components if component.type == "collision.collider")
    assert (overlay.x, overlay.y, overlay.width, overlay.height) == (100, 50, 50, 32)
    assert collision.data["layer"] == "player"
    assert collision.data["solid"] is False
    assert changed == [True]


def test_nw_handle_resizes_trigger_and_preserves_metadata():
    canvas = Canvas()
    changed = []
    target = entity()
    apply_box_trigger(target, 0, 0, 32, 20, "door.open", "player")
    controller = SceneCollisionController(canvas, target, on_change=lambda: changed.append(True))
    controller.render()
    controller.pointer_down(Event(100, 50))
    controller.pointer_move(Event(90, 40))
    controller.pointer_up(Event(90, 40))
    overlay = overlays_for_entity(target)[0]
    trigger = next(component for component in target.components if component.type == "collision.trigger")
    assert (overlay.x, overlay.y, overlay.width, overlay.height) == (90, 40, 42, 30)
    assert trigger.data["event"] == "door.open"
    assert trigger.data["filter_tag"] == "player"
    assert changed == [True]


def test_circle_radius_handle_resizes_collider_and_preserves_metadata():
    canvas = Canvas()
    changed = []
    target = entity()
    apply_circle_collider(target, 8, 6, 12, layer="player", solid=False)
    controller = SceneCollisionController(canvas, target, on_change=lambda: changed.append(True))
    controller.render()
    controller.pointer_down(Event(120, 56))
    controller.pointer_move(Event(138, 56))
    controller.pointer_up(Event(138, 56))
    overlay = overlays_for_entity(target)[0]
    collision = next(component for component in target.components if component.type == "collision.collider")
    assert (overlay.x, overlay.y, overlay.radius) == (108, 56, 30)
    assert collision.data["layer"] == "player"
    assert collision.data["solid"] is False
    assert changed == [True]


def test_zero_area_paint_is_ignored_without_change_callback():
    canvas = Canvas()
    changed = []
    target = entity()
    controller = SceneCollisionController(canvas, target, CollisionToolState(tool="collider"), lambda: changed.append(True))
    controller.pointer_down(Event(110, 60))
    controller.pointer_up(Event(110, 60))
    assert not any(component.type == "collision.collider" for component in target.components)
    assert changed == []
