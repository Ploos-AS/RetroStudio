from retrostudio.event_graph_workspace import EventGraphWorkspace


def test_trigger_exposes_event_property_and_updates_data():
    changed = []
    workspace = EventGraphWorkspace(on_change=lambda: changed.append(True))
    node = workspace.create_node("event.trigger")
    changed.clear()
    assert workspace.editable_properties() == ("event",)
    assert workspace.set_property("event", "player.enter")
    assert node.data["event"] == "player.enter"
    assert changed == [True]


def test_condition_exposes_property_and_value():
    workspace = EventGraphWorkspace()
    node = workspace.create_node("condition.equals")
    assert workspace.editable_properties() == ("property", "value")
    assert workspace.set_property("property", "player.keys")
    assert workspace.set_property("value", "3")
    assert node.data == {"property": "player.keys", "value": "3"}


def test_set_property_action_is_creator_editable():
    workspace = EventGraphWorkspace()
    node = workspace.create_node("action.set_property")
    assert workspace.set_property("property", "door.open")
    assert workspace.set_property("value", "true")
    assert node.data["property"] == "door.open"
    assert node.data["value"] == "true"


def test_nodes_without_properties_and_unknown_fields_are_noop():
    changed = []
    workspace = EventGraphWorkspace(on_change=lambda: changed.append(True))
    workspace.create_node("event.start")
    changed.clear()
    assert workspace.editable_properties() == ()
    assert not workspace.set_property("event", "ignored")
    assert changed == []


def test_setting_same_value_does_not_notify():
    changed = []
    workspace = EventGraphWorkspace(on_change=lambda: changed.append(True))
    node = workspace.create_node("action.emit_event")
    changed.clear()
    assert not workspace.set_property("event", node.data["event"])
    assert changed == []
