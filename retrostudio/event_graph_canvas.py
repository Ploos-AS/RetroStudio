"""Toolkit-neutral geometry and Tk-canvas compatible interaction for event graphs."""

from __future__ import annotations

from dataclasses import dataclass

from .event_graph import EventGraph, EventNode


@dataclass(frozen=True)
class NodeBounds:
    node_id: str
    left: float
    top: float
    right: float
    bottom: float

    def contains(self, x: float, y: float) -> bool:
        return self.left <= x <= self.right and self.top <= y <= self.bottom


class EventGraphCanvas:
    """Render, select, move and connect visual event graph nodes."""

    TAG = "retrostudio-event-graph"
    NODE_WIDTH = 160
    NODE_HEIGHT = 64
    PORT_RADIUS = 5

    def __init__(self, canvas, graph: EventGraph, on_change=None, on_select=None) -> None:
        self.canvas = canvas
        self.graph = graph
        self.on_change = on_change
        self.on_select = on_select
        self.selected_node_id: str | None = None
        self._drag = None
        self._connect_source: str | None = None

    def bounds(self, node: EventNode) -> NodeBounds:
        return NodeBounds(node.node_id, node.x, node.y, node.x + self.NODE_WIDTH, node.y + self.NODE_HEIGHT)

    def node_at(self, x: float, y: float) -> EventNode | None:
        for node in reversed(self.graph.nodes):
            if self.bounds(node).contains(float(x), float(y)):
                return node
        return None

    def output_port(self, node: EventNode) -> tuple[float, float]:
        bounds = self.bounds(node)
        return bounds.right, (bounds.top + bounds.bottom) / 2

    def input_port(self, node: EventNode) -> tuple[float, float]:
        bounds = self.bounds(node)
        return bounds.left, (bounds.top + bounds.bottom) / 2

    def render(self) -> None:
        self.canvas.delete(self.TAG)
        for link in self.graph.links:
            try:
                source = self.graph.node(link.source)
                target = self.graph.node(link.target)
            except ValueError:
                continue
            sx, sy = self.output_port(source)
            tx, ty = self.input_port(target)
            self.canvas.create_line(sx, sy, tx, ty, width=2, arrow="last", tags=(self.TAG, "event-link"))
        for node in self.graph.nodes:
            bounds = self.bounds(node)
            width = 3 if node.node_id == self.selected_node_id else 1
            self.canvas.create_rectangle(bounds.left, bounds.top, bounds.right, bounds.bottom, width=width, tags=(self.TAG, "event-node", f"event-node:{node.node_id}"))
            title = node.kind.replace(".", " / ").replace("_", " ").title()
            self.canvas.create_text(bounds.left + 10, bounds.top + 10, anchor="nw", text=title, tags=(self.TAG, "event-node-label"))
            self.canvas.create_text(bounds.left + 10, bounds.bottom - 10, anchor="sw", text=node.node_id, tags=(self.TAG, "event-node-id"))
            ix, iy = self.input_port(node)
            ox, oy = self.output_port(node)
            r = self.PORT_RADIUS
            self.canvas.create_oval(ix-r, iy-r, ix+r, iy+r, tags=(self.TAG, "event-input-port", f"event-input:{node.node_id}"))
            self.canvas.create_oval(ox-r, oy-r, ox+r, oy+r, tags=(self.TAG, "event-output-port", f"event-output:{node.node_id}"))

    def select(self, node_id: str | None) -> None:
        self.selected_node_id = node_id
        if self.on_select is not None:
            self.on_select(node_id)
        self.render()

    def begin_move(self, x: float, y: float) -> bool:
        node = self.node_at(x, y)
        if node is None:
            self.select(None)
            return False
        self.select(node.node_id)
        self._drag = (node.node_id, float(x) - node.x, float(y) - node.y)
        return True

    def update_move(self, x: float, y: float) -> None:
        if self._drag is None:
            return
        node_id, offset_x, offset_y = self._drag
        node = self.graph.node(node_id)
        node.x = float(x) - offset_x
        node.y = float(y) - offset_y
        self.render()

    def finish_move(self, x: float, y: float) -> bool:
        if self._drag is None:
            return False
        self.update_move(x, y)
        self._drag = None
        if self.on_change is not None:
            self.on_change()
        return True

    def begin_connect(self, source_node_id: str) -> None:
        self.graph.node(source_node_id)
        self._connect_source = source_node_id

    def finish_connect(self, target_node_id: str, outlet: str = "next") -> bool:
        if self._connect_source is None:
            return False
        source = self._connect_source
        self._connect_source = None
        if source == target_node_id:
            return False
        before = len(self.graph.links)
        self.graph.connect(source, target_node_id, outlet)
        changed = len(self.graph.links) != before
        if changed and self.on_change is not None:
            self.on_change()
        self.render()
        return changed
