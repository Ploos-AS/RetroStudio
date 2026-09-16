from retrostudio.model import Scene
from retrostudio.prefab_browser import PrefabBrowser
from retrostudio.prefab_placement import PrefabPlacementSession


def test_placement_preview_is_centered_on_pointer():
    session = PrefabPlacementSession(PrefabBrowser(), "platformer.player")
    preview = session.preview
    assert session.bounds_at(100, 80) == (
        100 - preview.width / 2,
        80 - preview.height / 2,
        100 + preview.width / 2,
        80 + preview.height / 2,
    )


def test_placement_commits_configured_template_at_pointer():
    scene = Scene("main", "Main")
    session = PrefabPlacementSession(
        PrefabBrowser(),
        "platformer.player",
        name="Hero",
        values={("behaviour.PlatformerPlayer", "speed"): 180},
    )
    entity = session.place(scene, 120, 90)
    preview = session.preview
    transform = entity.components[0]
    assert entity.name == "Hero"
    assert transform.data == {
        "x": round(120 - preview.width / 2),
        "y": round(90 - preview.height / 2),
    }
    player = next(item for item in entity.components if item.type == "behaviour.PlatformerPlayer")
    assert player.data["speed"] == 180
    assert session.active is False


def test_placement_is_single_use_and_can_be_cancelled():
    scene = Scene("main", "Main")
    session = PrefabPlacementSession(PrefabBrowser(), "action.projectile")
    session.cancel()
    assert session.active is False
    try:
        session.place(scene, 10, 10)
    except ValueError as exc:
        assert "no longer active" in str(exc)
    else:
        raise AssertionError("cancelled placement should fail")
