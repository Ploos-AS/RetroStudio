from retrostudio.event_graph import EventGraph
from retrostudio.event_graph_canvas import EventGraphCanvas, NODE_HEIGHT, NODE_WIDTH


class Canvas:
    def __init__(self):
        self.items = []
        self.coordinates = {}
        self.next_id = 1

    def delete(self, _tag):
        self.items = []

    def _add(self, kind, coords, **kwargs):
        item_id = self.next_id
        self.next_id += 1
        self.items.append((kind, coords, kwargs))
        self.coordinates[item_id] = list(coords)
        return item_id

    def create_line(self, *coords, **kwargs):
        return self._add("line", coords, **kwargs)

    def create_rectangle(self, *coords, **kwargs):
        return self._add("rectangle", coords, **kwargs)

    def create_text(self, *coords, **kwargs):
        return self._add("text", coords, **kwargs)

    def create_oval(self, *coords, **kwargs):
        return self._add("oval", coords, **kwargs)

    def coords(self, item_id, *coords):
        self.coordinates[item_id] = list(coords)


def graph():
    value = EventGraph()
    value.add_node("start", "event.start", 20, 30)
    value.add_node("action", "action.destroy", 300, 120)
    return value


def test_drag_output_to_input_creates_link_and_notifies():
    canvas = Canvas()
    changed = []
    value = graph()
    editor = EventGraphCanvas(canvas, value, on_change=lambda: changed.append(True))
    sx, sy = 20 + NODE_WIDTH, 30 + NODE_HEIGHT / 2
    tx, ty = 300, 120 + NODE_HEIGHT / 2
    assert editor.begin_gesture(sx, sy) == "link"
    editor.update_gesture(240, 100)
    assert editor.finish_gesture(tx, ty)
    assert [(link.source, link.target) for link in value.links] == [("start", "action")]
    assert changed == [True]


def test_link_preview_does_not_commit_when_released_on_empty_canvas():
    canvas = Canvas()
    changed = []
    value = graph()
    editor = EventGraphCanvas(canvas, value, on_change=lambda: changed.append(True))
    assert editor.begin_gesture(20 + NODE_WIDTH, 30 + NODE_HEIGHT / 2) == "link"
    editor.update_gesture(250, 250)
    assert not editor.finish_gesture(250, 250)
    assert value.links == []
    assert changed == []


def test_duplicate_link_is_rejected_without_change_notification():
    canvas = Canvas()
    changed = []
    value = graph()
    value.connect("start", "action")
    editor = EventGraphCanvas(canvas, value, on_change=lambda: changed.append(True))
    assert editor.begin_gesture(20 + NODE_WIDTH, 30 + NODE_HEIGHT / 2) == "link"
    assert not editor.finish_gesture(300, 120 + NODE_HEIGHT / 2)
    assert len(value.links) == 1
    assert changed == []
