"""Tk-neutral-in-behaviour canvas adapter for visual event graph editing."""

from __future__ import annotations

from .event_graph import EventGraph


NODE_WIDTH = 150
NODE_HEIGHT = 56
PORT_RADIUS = 6


class EventGraphCanvas:
    def __init__(self, canvas, graph: EventGraph, on_change=None, on_select=None) -> None:
        self.canvas = canvas
        self.graph = graph
        self.on_change = on_change
        self.on_select = on_select
        self.selected_node_id: str | None = None
        self._moving: tuple[str, float, float] | None = None
        self._linking_from: str | None = None
        self._link_preview = None

    def render(self) -> None:
        self.canvas.delete("event_graph")
        for link in self.graph.links:
            source = self.graph.node(link.source)
            target = self.graph.node(link.target)
            sx, sy = self._output_port(source)
            tx, ty = self._input_port(target)
            self.canvas.create_line(sx, sy, tx, ty, arrow="last", tags=("event_graph", "event_link"))
        for node in self.graph.nodes:
            selected = node.node_id == self.selected_node_id
            self.canvas.create_rectangle(
                node.x, node.y, node.x + NODE_WIDTH, node.y + NODE_HEIGHT,
                width=3 if selected else 1, tags=("event_graph", f"node:{node.node_id}"),
            )
            self.canvas.create_text(
                node.x + 10, node.y + NODE_HEIGHT / 2, anchor="w",
                text=node.kind.replace(".", " / "), tags=("event_graph", f"node:{node.node_id}"),
            )
            ix, iy = self._input_port(node)
            ox, oy = self._output_port(node)
            self.canvas.create_oval(ix - PORT_RADIUS, iy - PORT_RADIUS, ix + PORT_RADIUS, iy + PORT_RADIUS, tags=("event_graph", f"input:{node.node_id}"))
            self.canvas.create_oval(ox - PORT_RADIUS, oy - PORT_RADIUS, ox + PORT_RADIUS, oy + PORT_RADIUS, tags=("event_graph", f"output:{node.node_id}"))

    def begin_gesture(self, x: float, y: float) -> str | None:
        source = self.output_port_at(x, y)
        if source is not None:
            self._linking_from = source
            sx, sy = self._output_port(self.graph.node(source))
            self._link_preview = self.canvas.create_line(sx, sy, x, y, arrow="last", dash=(4, 3), tags=("event_graph", "link_preview"))
            return "link"
        node_id = self.node_at(x, y)
        if node_id is not None:
            node = self.graph.node(node_id)
            self.selected_node_id = node_id
            self._moving = (node_id, x - node.x, y - node.y)
            if self.on_select is not None:
                self.on_select(node_id)
            self.render()
            return "move"
        self.selected_node_id = None
        if self.on_select is not None:
            self.on_select(None)
        self.render()
        return None

    def update_gesture(self, x: float, y: float) -> None:
        if self._linking_from is not None:
            sx, sy = self._output_port(self.graph.node(self._linking_from))
            if self._link_preview is not None:
                self.canvas.coords(self._link_preview, sx, sy, x, y)
            return
        if self._moving is not None:
            node_id, dx, dy = self._moving
            self.graph.move_node(node_id, x - dx, y - dy)
            self.render()

    def finish_gesture(self, x: float, y: float) -> bool:
        if self._linking_from is not None:
            source = self._linking_from
            self._linking_from = None
            self._link_preview = None
            target = self.input_port_at(x, y)
            changed = False
            if target is not None and target != source:
                try:
                    self.graph.connect(source, target)
                    changed = True
                except ValueError:
                    changed = False
            self.render()
            if changed and self.on_change is not None:
                self.on_change()
            return changed
        if self._moving is not None:
            self._moving = None
            if self.on_change is not None:
                self.on_change()
            return True
        return False

    def begin_move(self, x: float, y: float) -> bool:
        return self.begin_gesture(x, y) == "move"

    def update_move(self, x: float, y: float) -> None:
        self.update_gesture(x, y)

    def finish_move(self, x: float, y: float) -> bool:
        return self.finish_gesture(x, y)

    def node_at(self, x: float, y: float) -> str | None:
        for node in reversed(self.graph.nodes):
            if node.x <= x <= node.x + NODE_WIDTH and node.y <= y <= node.y + NODE_HEIGHT:
                return node.node_id
        return None

    def output_port_at(self, x: float, y: float) -> str | None:
        return self._port_at(x, y, output=True)

    def input_port_at(self, x: float, y: float) -> str | None:
        return self._port_at(x, y, output=False)

    def _port_at(self, x: float, y: float, output: bool) -> str | None:
        for node in reversed(self.graph.nodes):
            px, py = self._output_port(node) if output else self._input_port(node)
            if (x - px) ** 2 + (y - py) ** 2 <= (PORT_RADIUS + 3) ** 2:
                return node.node_id
        return None

    @staticmethod
    def _input_port(node) -> tuple[float, float]:
        return node.x, node.y + NODE_HEIGHT / 2

    @staticmethod
    def _output_port(node) -> tuple[float, float]:
        return node.x + NODE_WIDTH, node.y + NODE_HEIGHT / 2
