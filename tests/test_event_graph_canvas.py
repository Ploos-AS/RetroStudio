from retrostudio.event_graph import EventGraph
from retrostudio.event_graph_canvas import EventGraphCanvas


class Canvas:
    def __init__(self):
        self.items = []

    def delete(self, tag):
        self.items = [item for item in self.items if tag not in item[-1]]

    def create_line(self, *args, **kwargs):
        self.items.append(("line", args, kwargs, kwargs.get("tags", ())))

    def create_rectangle(self, *args, **kwargs):
        self.items.append(("rectangle", args, kwargs, kwargs.get("tags", ())))

    def create_text(self, *args, **kwargs):
        self.items.append(("text", args, kwargs, kwargs.get("tags", ())))

    def create_oval(self, *args, **kwargs):
        self.items.append(("oval", args, kwargs, kwargs.get("tags", ())))


def graph():
    value = EventGraph()
    value.add_node("start", "event.start", 10, 20)
    value.add_node("action", "action.emit_event", 250, 40, event="door.open")
    return value


def test_render_draws_nodes_ports_and_links():
    canvas = Canvas()
    value = graph()
    value.connect("start", "action")
    editor = EventGraphCanvas(canvas, value)
    editor.render()
    kinds = [item[0] for item in canvas.items]
    assert kinds.count("rectangle") == 2
    assert kinds.count("oval") == 4
    assert kinds.count("line") == 1


def test_node_hit_testing_prefers_topmost_node():
    value = graph()
    value.add_node("top", "action.destroy", 20, 30)
    editor = EventGraphCanvas(Canvas(), value)
    assert editor.node_at(30, 40).node_id == "top"
    assert editor.node_at(900, 900) is None


def test_move_updates_canonical_node_position_and_notifies():
    changed = []
    selected = []
    value = graph()
    editor = EventGraphCanvas(Canvas(), value, on_change=lambda: changed.append(True), on_select=selected.append)
    assert editor.begin_move(20, 30)
    editor.update_move(60, 80)
    assert editor.finish_move(70, 90)
    node = value.node("start")
    assert (node.x, node.y) == (60, 80)
    assert selected == ["start"]
    assert changed == [True]


def test_clicking_empty_canvas_clears_selection():
    selected = []
    editor = EventGraphCanvas(Canvas(), graph(), on_select=selected.append)
    editor.select("start")
    assert not editor.begin_move(900, 900)
    assert editor.selected_node_id is None
    assert selected[-1] is None


def test_connect_creates_link_and_notifies_once():
    changed = []
    value = graph()
    editor = EventGraphCanvas(Canvas(), value, on_change=lambda: changed.append(True))
    editor.begin_connect("start")
    assert editor.finish_connect("action")
    assert [(link.source, link.target, link.outlet) for link in value.links] == [("start", "action", "next")]
    assert changed == [True]


def test_duplicate_and_self_links_are_non_destructive():
    changed = []
    value = graph()
    value.connect("start", "action")
    editor = EventGraphCanvas(Canvas(), value, on_change=lambda: changed.append(True))
    editor.begin_connect("start")
    assert not editor.finish_connect("action")
    editor.begin_connect("start")
    assert not editor.finish_connect("start")
    assert len(value.links) == 1
    assert changed == []
