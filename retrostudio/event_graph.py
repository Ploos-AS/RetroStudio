"""Platform-neutral visual event graph authoring model.

The graph describes creator intent only. Target backends decide how nodes and
connections become native runtime code or data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .model import Component, Diagnostic, Entity

EVENT_GRAPH_COMPONENT = "logic.event_graph"

NODE_KINDS = (
    "event.start",
    "event.trigger",
    "condition.equals",
    "action.set_property",
    "action.emit_event",
    "action.destroy",
)


@dataclass
class EventNode:
    node_id: str
    kind: str
    x: float = 0.0
    y: float = 0.0
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EventNode":
        return cls(node_id=str(raw["node_id"]), kind=str(raw["kind"]), x=float(raw.get("x", 0)), y=float(raw.get("y", 0)), data=dict(raw.get("data", {})))

    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "kind": self.kind, "x": self.x, "y": self.y, "data": self.data}


@dataclass(frozen=True)
class EventLink:
    source: str
    target: str
    outlet: str = "next"

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EventLink":
        return cls(str(raw["source"]), str(raw["target"]), str(raw.get("outlet", "next")))

    def to_dict(self) -> dict[str, str]:
        return {"source": self.source, "target": self.target, "outlet": self.outlet}


@dataclass
class EventGraph:
    nodes: list[EventNode] = field(default_factory=list)
    links: list[EventLink] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "EventGraph":
        return cls(nodes=[EventNode.from_dict(item) for item in raw.get("nodes", [])], links=[EventLink.from_dict(item) for item in raw.get("links", [])])

    def to_dict(self) -> dict[str, Any]:
        return {"nodes": [node.to_dict() for node in self.nodes], "links": [link.to_dict() for link in self.links]}

    def node(self, node_id: str) -> EventNode:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        raise ValueError(f"unknown event node: {node_id}")

    def add_node(self, node_id: str, kind: str, x: float = 0, y: float = 0, **data: Any) -> EventNode:
        if any(node.node_id == node_id for node in self.nodes):
            raise ValueError(f"duplicate event node: {node_id}")
        if kind not in NODE_KINDS:
            raise ValueError(f"unknown event node kind: {kind}")
        node = EventNode(node_id, kind, float(x), float(y), dict(data))
        self.nodes.append(node)
        return node

    def move_node(self, node_id: str, x: float, y: float) -> None:
        node = self.node(node_id)
        node.x = float(x)
        node.y = float(y)

    def connect(self, source: str, target: str, outlet: str = "next") -> EventLink:
        self.node(source)
        self.node(target)
        link = EventLink(source, target, outlet.strip() or "next")
        if link not in self.links:
            self.links.append(link)
        return link

    def remove_node(self, node_id: str) -> None:
        self.node(node_id)
        self.nodes[:] = [node for node in self.nodes if node.node_id != node_id]
        self.links[:] = [link for link in self.links if link.source != node_id and link.target != node_id]

    def diagnostics(self) -> list[Diagnostic]:
        out: list[Diagnostic] = []
        ids: set[str] = set()
        for node in self.nodes:
            path = f"nodes.{node.node_id}"
            if not node.node_id.strip():
                out.append(Diagnostic("error", "event_graph.node_id", "event node id is required", path))
            if node.node_id in ids:
                out.append(Diagnostic("error", "event_graph.duplicate_node", f"duplicate event node: {node.node_id}", path))
            ids.add(node.node_id)
            if node.kind not in NODE_KINDS:
                out.append(Diagnostic("error", "event_graph.node_kind", f"unknown event node kind: {node.kind}", path))
            if node.kind == "event.trigger" and not str(node.data.get("event", "")).strip():
                out.append(Diagnostic("error", "event_graph.trigger_event", "trigger event is required", path))
            if node.kind == "action.emit_event" and not str(node.data.get("event", "")).strip():
                out.append(Diagnostic("error", "event_graph.emit_event", "event name is required", path))
            if node.kind == "action.set_property" and not str(node.data.get("property", "")).strip():
                out.append(Diagnostic("error", "event_graph.property", "property name is required", path))
        for index, link in enumerate(self.links):
            path = f"links.{index}"
            if link.source not in ids:
                out.append(Diagnostic("error", "event_graph.link_source", f"unknown source node: {link.source}", path))
            if link.target not in ids:
                out.append(Diagnostic("error", "event_graph.link_target", f"unknown target node: {link.target}", path))
        return out


def graph_for_entity(entity: Entity) -> EventGraph:
    """Load the canonical event graph component for an entity, or an empty graph."""
    for component in entity.components:
        if component.type == EVENT_GRAPH_COMPONENT:
            return EventGraph.from_dict(component.data)
    return EventGraph()


def store_graph(entity: Entity, graph: EventGraph) -> None:
    """Create or replace an entity's canonical event graph component."""
    data = graph.to_dict()
    for component in entity.components:
        if component.type == EVENT_GRAPH_COMPONENT:
            component.data = data
            return
    entity.components.append(Component(EVENT_GRAPH_COMPONENT, data))
