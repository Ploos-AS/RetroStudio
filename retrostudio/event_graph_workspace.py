"""Creator-facing event graph workspace state, independent of Tk widgets."""

from __future__ import annotations

from .event_graph import EventGraph, NODE_KINDS


class EventGraphWorkspace:
    """Own palette actions, selection and property editing for the visual graph."""

    def __init__(self, graph: EventGraph | None = None, on_change=None) -> None:
        self.graph = graph or EventGraph()
        self.on_change = on_change
        self.selected_node_id: str | None = None
        self._sequence = 1

    @property
    def palette(self) -> tuple[str, ...]:
        return NODE_KINDS

    @property
    def selected_node(self):
        if self.selected_node_id is None:
            return None
        return self.graph.node(self.selected_node_id)

    def create_node(self, kind: str, x: float = 40, y: float = 40):
        prefix = kind.replace(".", "_")
        while True:
            node_id = f"{prefix}_{self._sequence}"
            self._sequence += 1
            if not any(node.node_id == node_id for node in self.graph.nodes):
                break
        data = {}
        if kind in ("event.trigger", "action.emit_event"):
            data["event"] = "event.name"
        elif kind == "condition.equals":
            data["property"] = "property.name"
            data["value"] = ""
        elif kind == "action.set_property":
            data["property"] = "property.name"
            data["value"] = ""
        node = self.graph.add_node(node_id, kind, x, y, **data)
        self.selected_node_id = node.node_id
        self._changed()
        return node

    def select(self, node_id: str | None) -> None:
        if node_id is not None:
            self.graph.node(node_id)
        self.selected_node_id = node_id

    def editable_properties(self) -> tuple[str, ...]:
        node = self.selected_node
        if node is None:
            return ()
        if node.kind in ("event.trigger", "action.emit_event"):
            return ("event",)
        if node.kind in ("condition.equals", "action.set_property"):
            return ("property", "value")
        return ()

    def set_property(self, name: str, value: str) -> bool:
        node = self.selected_node
        if node is None or name not in self.editable_properties():
            return False
        value = str(value)
        if node.data.get(name) == value:
            return False
        node.data[name] = value
        self._changed()
        return True

    def delete_selected(self) -> bool:
        if self.selected_node_id is None:
            return False
        node_id = self.selected_node_id
        self.graph.remove_node(node_id)
        self.selected_node_id = None
        self._changed()
        return True

    def _changed(self) -> None:
        if self.on_change is not None:
            self.on_change()
