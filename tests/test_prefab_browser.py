from retrostudio.model import Scene
from retrostudio.prefab_browser import PrefabBrowser


def test_browser_groups_creator_templates_by_genre():
    browser = PrefabBrowser()
    assert browser.genres == ("platformer", "adventure", "action")
    assert [item.prefab_id for item in browser.items("adventure")] == [
        "adventure.door",
        "adventure.dialogue_npc",
    ]


def test_browser_places_prefab_as_ordinary_scene_entity():
    browser = PrefabBrowser()
    scene = Scene("main", "Main")
    entity = browser.place(scene, "platformer.player", x=96, y=112)
    assert scene.entities == [entity]
    assert entity.components[0].type == "transform"
    assert entity.components[0].data == {"x": 96, "y": 112}
    assert any(component.type == "behaviour.PlatformerPlayer" for component in entity.components)


def test_browser_rejects_template_outside_its_catalogue():
    browser = PrefabBrowser(())
    scene = Scene("main", "Main")
    try:
        browser.place(scene, "platformer.player")
    except ValueError as exc:
        assert "not available" in str(exc)
    else:
        raise AssertionError("unavailable prefab should fail")
