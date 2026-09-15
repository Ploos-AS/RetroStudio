from pathlib import Path


def test_collision_toolbar_exposes_creator_tools_without_target_logic():
    source = Path("retrostudio/collision_toolbar.py").read_text(encoding="utf-8")
    assert '"select", "Select"' in source
    assert '"collider", "Collider"' in source
    assert '"trigger", "Trigger"' in source
    assert "CollisionToolState" in source
    assert "backend" not in source.lower()
    assert "amiga" not in source.lower()
    assert "atari" not in source.lower()


def test_toolbar_exposes_layer_event_and_filter_fields():
    source = Path("retrostudio/collision_toolbar.py").read_text(encoding="utf-8")
    assert "collider_layer" in source
    assert "trigger_event" in source
    assert "trigger_filter" in source
    assert "def sync(" in source
