from retrostudio.event_graph import EventGraph, EventLink, EventNode


def test_graph_roundtrip_is_plain_project_data():
    graph = EventGraph()
    graph.add_node("start", "event.start", 10, 20)
    graph.add_node("open", "action.emit_event", 120, 20, event="door.open")
    graph.connect("start", "open")
    restored = EventGraph.from_dict(graph.to_dict())
    assert restored == graph


def test_connect_validates_nodes_and_deduplicates_links():
    graph = EventGraph([EventNode("a", "event.start"), EventNode("b", "action.destroy")])
    graph.connect("a", "b")
    graph.connect("a", "b")
    assert graph.links == [EventLink("a", "b", "next")]


def test_remove_node_removes_attached_links():
    graph = EventGraph()
    graph.add_node("start", "event.start")
    graph.add_node("condition", "condition.equals")
    graph.add_node("action", "action.destroy")
    graph.connect("start", "condition")
    graph.connect("condition", "action", "true")
    graph.remove_node("condition")
    assert [node.node_id for node in graph.nodes] == ["start", "action"]
    assert graph.links == []


def test_diagnostics_report_creator_errors():
    graph = EventGraph(
        nodes=[
            EventNode("trigger", "event.trigger"),
            EventNode("emit", "action.emit_event"),
            EventNode("set", "action.set_property"),
        ],
        links=[EventLink("missing", "emit")],
    )
    codes = {item.code for item in graph.diagnostics()}
    assert "event_graph.trigger_event" in codes
    assert "event_graph.emit_event" in codes
    assert "event_graph.property" in codes
    assert "event_graph.link_source" in codes


def test_unknown_node_kind_is_diagnostic_when_loading_existing_data():
    graph = EventGraph.from_dict({"nodes": [{"node_id": "legacy", "kind": "old.custom"}]})
    assert [item.code for item in graph.diagnostics()] == ["event_graph.node_kind"]
