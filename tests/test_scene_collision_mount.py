from pathlib import Path


def test_mount_adapter_keeps_desktop_wiring_concise():
    source = Path("retrostudio/scene_collision_mount.py").read_text()
    assert "CollisionToolbar" in source
    assert "SceneCollisionController" in source
    assert "controller.bind()" in source
    assert "controller.render()" in source
    assert "toolbar.sync()" in source


def test_mount_adapter_reports_creator_facing_tool_status():
    source = Path("retrostudio/scene_collision_mount.py").read_text()
    assert "Collision tool: Select" in source
    assert "Collision tool: Collider" in source
    assert "Collision tool: Trigger" in source
