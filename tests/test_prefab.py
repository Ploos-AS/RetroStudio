from retrostudio.prefab import PREFABS, instantiate_prefab, prefab, prefabs_for_genre
from retrostudio.model import Scene


def test_baseline_prefabs_cover_multiple_creator_genres():
    assert {item.genre for item in PREFABS} >= {"platformer", "adventure", "action"}
    assert prefab("platformer.player").name == "Player"
    assert len(prefabs_for_genre("platformer")) >= 3


def test_platformer_player_is_composed_from_canonical_components():
    scene = Scene("main", "Main")
    entity = instantiate_prefab(scene, "platformer.player", x=24, y=48)
    types = [component.type for component in entity.components]
    assert types == ["transform", "behaviour.PlatformerPlayer", "behaviour.CameraFollow", "collision.collider"]
    assert entity.components[0].data == {"x": 24, "y": 48}
    assert entity.components[1].data["speed"] == 120
    assert entity.components[-1].data["shape"]["height"] == 28


def test_prefab_instances_are_deeply_independent():
    scene = Scene("main", "Main")
    first = instantiate_prefab(scene, "adventure.dialogue_npc")
    second = instantiate_prefab(scene, "adventure.dialogue_npc")
    first.components[1].data["text"] = "Changed"
    assert second.components[1].data["text"] == "Hello!"
    assert first.entity_id != second.entity_id


def test_explicit_entity_id_is_made_unique_without_overwriting():
    scene = Scene("main", "Main")
    first = instantiate_prefab(scene, "action.projectile", entity_id="shot")
    second = instantiate_prefab(scene, "action.projectile", entity_id="shot")
    assert first.entity_id == "shot"
    assert second.entity_id == "shot-2"
    assert scene.entities == [first, second]


def test_unknown_prefab_is_rejected():
    try:
        prefab("missing")
    except ValueError as exc:
        assert "unknown prefab" in str(exc)
    else:
        raise AssertionError("unknown prefab should fail")
