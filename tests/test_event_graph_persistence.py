from retrostudio.event_graph import EVENT_GRAPH_COMPONENT, EventGraph, graph_for_entity, store_graph
from retrostudio.model import Component, Entity


def test_missing_component_loads_empty_graph_without_mutating_entity():
    entity = Entity("player", "Player")
    graph = graph_for_entity(entity)
    assert graph == EventGraph()
    assert entity.components == []


def test_store_creates_canonical_event_graph_component():
    entity = Entity("player", "Player")
    graph = EventGraph()
    graph.add_node("start", "event.start", 12, 34)
    store_graph(entity, graph)
    assert len(entity.components) == 1
    assert entity.components[0].type == EVENT_GRAPH_COMPONENT
    assert graph_for_entity(entity) == graph


def test_store_replaces_existing_component_and_preserves_other_components():
    entity = Entity(
        "door",
        "Door",
        [Component("visual.sprite", {"asset": "door.png"}), Component(EVENT_GRAPH_COMPONENT, {"nodes": [], "links": []})],
    )
    graph = EventGraph()
    graph.add_node("trigger", "event.trigger", 20, 40, event="player.enter")
    graph.add_node("open", "action.set_property", 240, 40, property="door.open", value="true")
    graph.connect("trigger", "open")
    store_graph(entity, graph)
    assert [component.type for component in entity.components] == ["visual.sprite", EVENT_GRAPH_COMPONENT]
    restored = graph_for_entity(entity)
    assert restored == graph
    assert restored.nodes[0].x == 20
    assert restored.nodes[1].data["value"] == "true"
    assert restored.links[0].source == "trigger"


def test_loaded_graph_is_detached_until_explicit_store():
    entity = Entity("npc", "NPC", [Component(EVENT_GRAPH_COMPONENT, {"nodes": [], "links": []})])
    graph = graph_for_entity(entity)
    graph.add_node("start", "event.start")
    assert entity.components[0].data["nodes"] == []
    store_graph(entity, graph)
    assert entity.components[0].data["nodes"][0]["node_id"] == "start"
