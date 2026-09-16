from retrostudio.event_graph_workspace import EventGraphWorkspace


def test_palette_exposes_creator_node_kinds():
    workspace = EventGraphWorkspace()
    assert "event.start" in workspace.palette
    assert "condition.equals" in workspace.palette
    assert "action.emit_event" in workspace.palette


def test_create_node_generates_unique_ids_and_valid_defaults():
    changed = []
    workspace = EventGraphWorkspace(on_change=lambda: changed.append(True))
    first = workspace.create_node("event.trigger", 10, 20)
    second = workspace.create_node("event.trigger", 30, 40)
    assert first.node_id != second.node_id
    assert first.data["event"] == "event.name"
    assert workspace.selected_node_id == second.node_id
    assert workspace.graph.diagnostics() == []
    assert changed == [True, True]


def test_delete_selected_removes_links_and_notifies():
    changed = []
    workspace = EventGraphWorkspace(on_change=lambda: changed.append(True))
    start = workspace.create_node("event.start")
    action = workspace.create_node("action.destroy")
    workspace.graph.connect(start.node_id, action.node_id)
    workspace.select(start.node_id)
    assert workspace.delete_selected()
    assert [node.node_id for node in workspace.graph.nodes] == [action.node_id]
    assert workspace.graph.links == []
    assert workspace.selected_node_id is None
    assert len(changed) == 3


def test_delete_without_selection_is_noop():
    changed = []
    workspace = EventGraphWorkspace(on_change=lambda: changed.append(True))
    assert not workspace.delete_selected()
    assert changed == []
