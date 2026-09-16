from retrostudio.model import Scene
from retrostudio.prefab_browser import PrefabBrowser


def test_browser_groups_creator_templates_by_genre():
    browser = PrefabBrowser()
    assert browser.genres == ("platformer", "adventure", "action")
    assert [item.prefab_id for item in browser.items("adventure")] == ["adventure.door", "adventure.dialogue_npc"]


def test_browser_exposes_description_and_creator_fields():
    browser = PrefabBrowser()
    definition = browser.definition("platformer.enemy_patrol")
    assert "patrol" in definition.description.lower()
    fields = browser.fields(definition.prefab_id)
    assert [(field.key, field.field_type) for field in fields] == [("speed", "number"), ("distance", "number"), ("axis", "choice")]
    assert fields[-1].choices == ("x", "y")


def test_browser_preview_reports_footprint_collision_and_features():
    preview = PrefabBrowser().preview("platformer.player")
    assert (preview.width, preview.height) == (16.0, 28.0)
    assert preview.collision_shape == "box"
    assert preview.features == ("PlatformerPlayer", "CameraFollow")


def test_browser_preview_uses_placeholder_footprint_without_collider():
    preview = PrefabBrowser().preview("platformer.collectible")
    assert (preview.width, preview.height) == (32.0, 32.0)
    assert preview.collision_shape is None
    assert preview.features == ("Collectible",)


def test_browser_places_configured_prefab_as_ordinary_scene_entity():
    browser = PrefabBrowser()
    scene = Scene("main", "Main")
    entity = browser.place(scene, "platformer.player", x=96, y=112, name="Hero", values={("behaviour.PlatformerPlayer", "speed"): 180})
    assert scene.entities == [entity]
    assert entity.name == "Hero"
    assert entity.components[0].type == "transform"
    assert entity.components[0].data == {"x": 96, "y": 112}
    player = next(component for component in entity.components if component.type == "behaviour.PlatformerPlayer")
    assert player.data["speed"] == 180


def test_browser_rejects_template_outside_its_catalogue():
    browser = PrefabBrowser(())
    scene = Scene("main", "Main")
    try:
        browser.place(scene, "platformer.player")
    except ValueError as exc:
        assert "not available" in str(exc)
    else:
        raise AssertionError("unavailable prefab should fail")
