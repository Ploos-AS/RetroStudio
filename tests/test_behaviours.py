import pytest

from retrostudio.behaviours import (
    BEHAVIOUR_TYPES,
    BehaviourDefinition,
    add_behaviour,
    entity_behaviours,
    remove_behaviour,
)
from retrostudio.model import Entity


def test_baseline_behaviours_are_available():
    assert BEHAVIOUR_TYPES == (
        "PlatformerPlayer",
        "CameraFollow",
        "EnemyPatrol",
        "Collectible",
        "Door",
        "Projectile",
    )


def test_platformer_player_defaults_round_trip_through_component():
    entity = Entity("player", "Player")
    component = add_behaviour(entity, BehaviourDefinition("PlatformerPlayer"))
    assert component.type == "behaviour.PlatformerPlayer"
    assert component.data["speed"] == 120
    assert component.data["jump_speed"] == 260
    behaviours = entity_behaviours(entity)
    assert behaviours[0].behaviour_type == "PlatformerPlayer"
    assert behaviours[0].normalized_values()["gravity"] == 700


def test_behaviour_values_can_be_customized():
    definition = BehaviourDefinition("EnemyPatrol", {"speed": 80, "axis": "y"})
    assert definition.validate() == []
    values = definition.normalized_values()
    assert values["speed"] == 80
    assert values["axis"] == "y"
    assert values["distance"] == 96


def test_duplicate_behaviour_is_rejected():
    entity = Entity("door", "Door")
    add_behaviour(entity, BehaviourDefinition("Door"))
    with pytest.raises(ValueError, match="already has behaviour"):
        add_behaviour(entity, BehaviourDefinition("Door"))


def test_invalid_behaviour_values_report_diagnostics():
    diagnostics = BehaviourDefinition("EnemyPatrol", {"axis": "diagonal"}).validate()
    assert diagnostics[0].code == "behaviour.axis_invalid"
    diagnostics = BehaviourDefinition("Projectile", {"lifetime_ms": 0}).validate()
    assert diagnostics[0].code == "behaviour.lifetime_invalid"


def test_remove_behaviour():
    entity = Entity("coin", "Coin")
    add_behaviour(entity, BehaviourDefinition("Collectible"))
    assert remove_behaviour(entity, "Collectible") is True
    assert entity_behaviours(entity) == []
    assert remove_behaviour(entity, "Collectible") is False
